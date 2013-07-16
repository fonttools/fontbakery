import logging
import os
import subprocess
import yaml
from flask import json # require Flask > 0.10
from flask.ext.rq import job
import plistlib
from .decorators import cached
import checker.runner

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
DATA_ROOT = os.path.join(ROOT, 'data')

CLONE_PREPARE_SH = """mkdir -p %(login)s/%(project_id)s.in/ && mkdir -p %(login)s/%(project_id)s.out/src/"""
CLONE_SH = """git clone --depth=100 --quiet --branch=master %(clone)s ."""
CLEAN_SH = '' #"""cd %(root)s && rm -rf %(login)s/%(project_id)s.in/ && rm -rf %(login)s/%(project_id)s.out/"""

logger = logging.getLogger('bakery.tasks')
logger.setLevel(logging.INFO)

def run(*args, **kw):
    logger.info("%s %s" % (str(args), str(kw)))
    out = subprocess.check_output(*args, **kw)
    logger.info(out)

def prun(*args, **kw):
    logger.info("%s %s" % (str(args), str(kw)))
    return subprocess.Popen(*args, **kw)

def add_logger(login, project_id):
    fh = logging.FileHandler(os.path.join(DATA_ROOT, '%(login)s/process.%(project_id)s.log' % locals()))
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.info('='*80)
    return(fh)

def remove_logger(fh):
    logger.removeHandler(fh)

@job
def clone_and_process(project):
    git_clone(login = project.login, project_id = project.id, clone = project.clone)
    process_project(login = project.login, project_id = project.id)


@job
def logged_process(project):
    # fh = add_logger(login = project.login, project_id = project.id)
    # # push check before project process
    project_state_push(login = project.login, project_id = project.id)
    process_project(login = project.login, project_id = project.id)
    # remove_logger(fh)

@job
def git_clone(login, project_id, clone):
    git_clean(login, project_id)
    params = {'login': login,
        'project_id': project_id,
        }
    project_dir = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % params)
    if os.path.exists(project_dir):
        run('git pull origin master', shell= True, cwd=project_dir)
    else:
        run(CLONE_PREPARE_SH % params, shell=True, cwd=DATA_ROOT)
        # clone variable considered unsafe
        run(str(CLONE_SH % {'clone': clone}).split(), shell=False,
            cwd=os.path.join(DATA_ROOT, login, str(project_id)+'.in/'))

def git_clean(login, project_id):
    params = locals()
    params['root'] = DATA_ROOT
    run(CLEAN_SH % params, shell=True)

def check_yaml(login, project_id):
    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals(), 'bakery.yaml')
    if not os.path.exists(yml):
        return 0
    return 1

def rwalk(path):
    h = {}
    cd = os.path.abspath(path)
    fs = os.listdir(path)
    for f in fs:
        cf = os.path.join(cd, f)
        if os.path.isfile(cf):
            h[f] = {}
        elif os.path.isdir(cf) and not cf.endswith('.git'):
            h[f] = rwalk(cf)
    return h

# @cached
def project_state_get(login, project_id, full=False):
    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % locals())
    dir_in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    if os.path.exists(yml):
        state = yaml.load(open(yml, 'r').read())
    else:
        state = yaml.load(open(os.path.join(ROOT, 'bakery', 'bakery.defaults.yaml'), 'r').read()) # the same dir

    if not full:
        # don't need to walk over all usef folders
        return state

    txt_files = []
    ufo_dirs = []
    l = len(dir_in)
    for root, dirs, files in os.walk(dir_in):
        for f in files:
            fullpath = os.path.join(root, f)
            if os.path.splitext(fullpath)[1].lower() in ['.txt', '.md', '.markdown', 'LICENSE']:
                txt_files.append(fullpath[l:])
        for d in dirs:
            fullpath = os.path.join(root, d)
            if os.path.splitext(fullpath)[1].lower() == '.ufo':
                ufo_dirs.append(fullpath[l:])

    state['txt_files'] = txt_files
    state['ufo_dirs'] = ufo_dirs

    if os.path.exists(state['license_file']):
        state['license_file_found'] = True

    return state

def project_state_save(login, project_id, state):
    yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % locals())
    f = open(yml, 'w')
    f.write(yaml.safe_dump(state))
    f.close()

@job
def project_state_push(login, project_id):
    # TODO fix this
    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    try:
        if prun("git rev-list HEAD...origin/master --count") != '0':
            # pull needed, remote is updated
            return False
        else:
            run("git add bakery.yaml; git commit -m 'bakery.yaml robot update'", shell=True, cwd=_in)
            run("git push origin master", shell=True, cwd=_in)
            return True
    except subprocess.CalledProcessError:
        return False

@job
def process_project(login, project_id):
    state = project_state_get(login, project_id)
    # yml = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % locals())
    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())
    # if os.path.exists(yml):
    #     # copy .bakery.yml
    #     run(['cp', yml, os.path.join(_out, 'bakery.yaml')])
    for ufo, name in state['out_ufo'].items():
        if state['rename']:
            ufo_folder = name+'.ufo'
        else:
            ufo_folder = ufo.split('/')[-1]
        run(['cp', '-R', os.path.join(_in, ufo), os.path.join(_out, ufo_folder)])
        if state['rename']:
            finame = os.path.join(_out, ufo_folder, 'fontinfo.plist')
            finfo = plistlib.readPlist(finame)
            finfo['familyName'] = name
            plistlib.writePlist(finfo, finame)

    # set of other commands
    if state['autoprocess']:
        # project should be processes only when setup is done
        generate_fonts(login, project_id)
        ttfautohint_process(login, project_id)
        # subset
        subset_process(login, project_id)
        generate_metadata(login, project_id)
        lint_process(login, project_id)

def status(login, project_id):
    if not check_yaml(login, project_id):
        return 0

def read_license(login, project_id):
    state = project_state_get(login, project_id, full=True)
    licensef = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals(), state['license_file'])
    if os.path.exists(licensef):
        try:
            return unicode(open(licensef, 'r').read(), "utf8")
        except IOError:
            return "Error reading license file"
    else:
        return None

def read_metadata(login, project_id):
    metadata = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json')
    metadata_new = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json.new')

    if os.path.exists(metadata):
        metadata_file = unicode(open(metadata, 'r').read(), "utf8")
    else:
        metadata_file = ''

    if os.path.exists(metadata_new):
        metadata_new_file = unicode(open(metadata_new, 'r').read(), "utf8")
    else:
        metadata_new_file = ''

    return (metadata_file, metadata_new_file)

def save_metadata(login, project_id, metadata, del_new=True):
    mf = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json')
    mf_new = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'METADATA.json.new')

    f = open(mf, 'w')
    json.dump(json.loads(metadata), f, indent=2, ensure_ascii=True) # same params as in generatemetadata.py
    f.close()

    if del_new:
        if os.path.exists(mf_new):
            os.remove(mf_new)

def read_description(login, project_id):
    description_file = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'DESCRIPTION.en_us.html')

    if os.path.exists(description_file):
        description = unicode(open(description_file, 'r').read(), "utf8")
    else:
        description = ''

    return description


def save_description(login, project_id, description):
    mf = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals(), 'DESCRIPTION.en_us.html')

    f = open(mf, 'w')
    f.write(description)
    f.close()

def read_log(login, project_id):
    log_file = os.path.join(DATA_ROOT, '%(login)s/process.%(project_id)s.log' % locals())

    if os.path.exists(log_file):
        return unicode(open(log_file, 'r').read(), "utf8")
    else:
        return ''

def read_yaml(login, project_id):
    yaml_file = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/bakery.yaml' % locals())

    if os.path.exists(yaml_file):
        return unicode(open(yaml_file, 'r').read(), "utf8")
    else:
        return ''

def read_tree(login, project_id):
    return rwalk(os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals()))

def generate_fonts(login, project_id):
    state = project_state_get(login, project_id)
    _in = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.in/' % locals())
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())

    # child = prun('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE, cwd=_in)
    # hashno = child.stdout.readline().strip()

    scripts_folder = os.path.join(ROOT, 'scripts')

    for name in state['out_ufo'].values():
        # this command generate file with commit hash in file name
        # cmd = "python ufo2ttf.py '%(in)s' '%(out)s.%(hashno)s.ttf' '%(out)s.%(hashno)s.otf'" % {
        #     'in':os.path.join(_out, name+'.ufo'),
        #     'out': os.path.join(_out, name),
        #     'hashno': hashno
        # }
        cmd_short = "python ufo2ttf.py '%(out)s.ufo' '%(out)s.ttf' '%(out)s.otf'" % {
            'in':os.path.join(_in, name+'.ufo'),
            'out': os.path.join(_out, name),
        }
        # run(cmd, shell=True, cwd = scripts_folder)
        run(cmd_short, shell=True, cwd = scripts_folder)

def generate_metadata(login, project_id):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    cmd = "%(wd)s/venv/bin/python %(wd)s/scripts/genmetadata.py '%(out)s'"
    print(cmd % {'wd': ROOT, 'out': _out})
    run(cmd % {'wd': ROOT, 'out': _out} , shell=True, cwd=_out)

def lint_process(login, project_id):
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    # java -jar dist/lint.jar "$(dirname $metadata)"
    cmd = "java -jar %(wd)s/scripts/lint.jar '%(out)s'"
    run(cmd % {'wd': ROOT, 'out': _out} , shell=True, cwd=_out)

def ttfautohint_process(login, project_id):
    # $ ttfautohint -l 7 -r 28 -G 0 -x 13 -w "" -W -c original_font.ttf final_font.ttf
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    if state['ttfautohintuse']:
        for name in state['out_ufo'].values():
            cmd = "ttfautohint '%(src)s.ttf' '%(out)s.ttf'" % {
                'out': os.path.join(_out, name),
                'src': os.path.join(_out, 'src', name),
            }
            run(cmd % {'wd': ROOT, 'out': _out}, shell=True, cwd=_out)
    else:
        run("cp src/*.ttf .", shell=True, cwd=_out)

def subset_process(login, project_id):
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/' % locals())
    for subset in state['subset']:
        for name in state['out_ufo'].values():
            # python ~/googlefontdirectory/tools/subset/subset.py \
            #   --null --nmr --roundtrip --script --subset=$subset \
            #   $font.ttf $font.$subset >> $font.$subset.log \
            # 2>> $font.$subset.log; \

            cmd = str("%(wd)s/venv/bin/python %(wd)s/scripts/subset.py --null " + \
                  "--nmr --roundtrip --script --subset=%(subset)s '%(out)s.ttf'" + \
                  " %(out)s.%(subset)s") % {
                'subset':subset,
                'out': os.path.join(_out, name),
                'name': name,
                'wd': ROOT
            }
            run(cmd, shell=True, cwd=_out)
    run("for i in *+latin; do mv $i $(echo $i | sed 's/+latin//g'); done ", shell=True, cwd=_out)

def project_tests(login, project_id):
    state = project_state_get(login, project_id)
    _out = os.path.join(DATA_ROOT, '%(login)s/%(project_id)s.out/src/' % locals())
    result = {}
    for name in state['out_ufo'].values():
        result[name] = checker.runner.run_set(os.path.join(_out, name+'.ufo'))
    return result

