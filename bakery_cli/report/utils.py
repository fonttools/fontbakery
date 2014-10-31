import json
import fnmatch
import os.path as op
import os
import sys
import subprocess
import shutil
import six
from jinja2 import Environment, FileSystemLoader

try:
    import urllib.parse as urllib_parse
except ImportError:
    from urllib import urlencode as urllib_parse


GH = 'https://github.com'
GH_RAW = 'https://raw.githubusercontent.com/'
TEMPLATE_DIR = op.join(op.dirname(__file__), 'templates')
BUILD_INFO_DIR = op.join(op.dirname(__file__), 'build_info')
jinjaenv = Environment(loader=FileSystemLoader(TEMPLATE_DIR),
                       extensions=["jinja2.ext.do", ],
                       autoescape=True)


def render_template(templatename, *args, **kwargs):
    template = jinjaenv.get_template(templatename)
    return template.render(*args, **kwargs).encode('utf8')


def _build_repo_url(base_url, *chunks, **kwargs):
    repo_slug = os.environ.get('TRAVIS_REPO_SLUG', 'fontdirectory/dummy')
    if kwargs:
        return '{}?{}'.format(op.join(base_url, repo_slug, *chunks), urllib_parse(kwargs))
    return op.join(base_url, repo_slug, *chunks)


def build_fontbakery_url(*chunks):
    return op.join(GH, 'googlefonts', 'fontbakery', *chunks)


def build_repo_url(*chunks, **kwargs):
    return _build_repo_url(GH, *chunks, **kwargs)


def build_raw_repo_url(*chunks, **kwargs):
    return _build_repo_url(GH_RAW, *chunks, **kwargs)


jinjaenv.globals['build_repo_url'] = build_repo_url
jinjaenv.globals['build_raw_repo_url'] = build_raw_repo_url


def prun(command, cwd, log=None):
    """
    Wrapper for subprocess.Popen that capture output and return as result

        :param command: shell command to run
        :param cwd: current working dir
        :param log: loggin object with .write() method

    """
    # print the command on the worker console
    print("[%s]:%s" % (cwd, command))
    env = os.environ.copy()
    env.update({'PYTHONPATH': os.pathsep.join(sys.path)})
    process = subprocess.Popen(command, shell=True, cwd=cwd,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               close_fds=True, env=env)
    if log:
        log.write('$ %s\n' % command)

    stdout = ''
    for line in iter(process.stdout.readline, ''):
        if log:
            log.write(line)
        stdout += line
        process.stdout.flush()
    return stdout


def git_info(config):
    """ If application is under git then return commit's hash
        and timestamp of the version running.

        Return None if application is not under git."""
    params = "git log -n1"
    fmt = """ --pretty=format:'{"hash":"%h", "commit":"%H","date":"%cd"}'"""
    log = prun(params + fmt, cwd=config['path'])
    try:
        return json.loads(log)
    except ValueError:
        return None


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class lazy_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        result = self.func(instance)
        setattr(instance, self.func.__name__, result)
        return result


class ReportPageBase(object):
    name = None

    def __init__(self, build_info):
        self.build_info = build_info
        self.path = op.join(self.build_info.pages_dir, self.name)
        if not op.exists(self.path):
            os.makedirs(self.path)

    def copy_file(self, src, alt_name=None):
        dst = self.path if not alt_name else op.join(self.path, alt_name)
        self.build_info.copy_file(src, dst)

    def dump_file(self, data, fname, **kwargs):
        self.build_info.dump_file(data, op.join(self.path, fname), **kwargs)

    def write_file(self, data, fname):
        self.build_info.write_file(data, op.join(self.path, fname))

    def wrap_with_jsonp_callback(self, callback, fname):
        with open(fname, "r+") as f:
            data = f.read()
            f.seek(0)
            f.write('{callback}({data})'.format(callback=callback, data=data))
            f.truncate()


class SummaryPage(ReportPageBase):
    name = 'summary'


class BuildPage(ReportPageBase):
    name = 'build'


class MetadataPage(ReportPageBase):
    name = 'metadata'


class DescriptionPage(ReportPageBase):
    name = 'description'


class BakeryYamlPage(ReportPageBase):
    name = 'bakery-yaml'


class TestsPage(ReportPageBase):
    name = 'tests'


class ChecksPage(ReportPageBase):
    name = 'checks'


class ReviewPage(ReportPageBase):
    name = 'review'


class BuildInfo(six.with_metaclass(Singleton, object)):
    def __init__(self, config, **kwargs):
        self.config = config
        self.repo_slug = os.environ.get('TRAVIS_REPO_SLUG', 'fontdirectory/dummy')
        self.source_dir = kwargs.get('source_dir', BUILD_INFO_DIR)
        self.build_dir = kwargs.get('build_dir', self.config['path'])
        self.target_dir = kwargs.get('target_dir', op.join(self.config['path'], 'build_info'))
        self.data_dir = kwargs.get('data_dir', op.join(self.target_dir, 'data'))
        self.pages_dir = kwargs.get('pages_dir', op.join(self.data_dir, 'pages'))
        self.static_dir = kwargs.get('static_dir', op.join(self.target_dir, 'static'))
        self.css_dir = kwargs.get('css_dir', op.join(self.static_dir, 'css'))

        self.init()
        self.build_page = BuildPage(self)
        self.metadata_page = MetadataPage(self)
        self.description_page = DescriptionPage(self)
        self.bakeryyaml_page = BakeryYamlPage(self)
        self.tests_page = TestsPage(self)
        self.checks_page = ChecksPage(self)
        self.summary_page = SummaryPage(self)
        self.review_page = ReviewPage(self)

        print('Build info added.')
        self.write_build_info()
        self.write_index_file()
        self.write_readme_file()
        # self.bower_install(components=kwargs.get('bower_components', ()))

    def bower_install(self, components=()):
        #TODO dependency on bower is temporary
        #cdn is preferred, if js can't be on cdn, it will be in static data
        print('Installing components')
        components_lst = components or ['angular-bootstrap',
                                        'angular-sanitize',
                                        'angular-moment --save',
                                        'https://github.com/andriyko/ui-ace.git#bower',
                                        'https://github.com/andriyko/angular-route-styles.git',
                                        'ng-table']
        params = ' '.join(components_lst)
        log = prun('bower install {}'.format(params), self.static_dir)
        print(log)

    def exists(self):
        return op.exists(self.target_dir)

    def clean(self):
        if self.exists():
            shutil.rmtree(self.target_dir)

    def init(self):
        self.clean()
        shutil.copytree(self.source_dir, self.target_dir)
        self.copy_ttf_fonts()

    def copy_file(self, src, dst):
        try:
            print('Copying file: {} -> {}'.format(src, dst))
            shutil.copy2(src, dst)
        except shutil.Error as e:
            print('Error: %s' % e)
        except IOError as e:
            print('Error: %s' % e.strerror)

    def move_file(self, src, dst):
        try:
            print('Moving file: {} -> {}'.format(src, dst))
            shutil.move(src, dst)
        except shutil.Error as e:
            print('Error: %s' % e)
        except IOError as e:
            print('Error: %s' % e.strerror)

    def copy_to_data(self, src):
        self.copy_file(src, self.data_dir)

    def move_to_data(self, src):
        self.move_file(src, self.data_dir)

    def dump_data_file(self, data, fname):
        print('Dumping data to file: {}'.format(fname))
        with open(op.join(self.data_dir, fname), 'w') as outfile:
            json.dump(data, outfile, indent=2)

    def dump_file(self, data, fpath, **kwargs):
        print('Dumping data to file: {}'.format(fpath))
        kwargs.setdefault('indent', 2)
        with open(fpath, 'w') as outfile:
            json.dump(data, outfile, **kwargs)

    def write_file(self, data, fpath, mode='w'):
        print('Writing data to file: {}'.format(fpath))
        with open(fpath, mode) as outfile:
            outfile.write(data)

    def write_build_info(self):
        travis_link = 'https://travis-ci.org/{}'.format(self.repo_slug)
        info = self.version
        info.update(dict(build_passed=not self.config.get('failed', False), travis_link=travis_link))
        self.dump_data_file(info, 'build_info.json')
        self.dump_data_file(self.repo, 'repo.json')

    def write_index_file(self):
        tmpl = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="0; url=http://fontdirectory.github.io/collection/#/{slug}/" />"
            <title>{title}</title>
        </head>
        <body>
        </body>
        </html>""".format(slug=self.repo_slug, title=self.repo_slug)
        self.write_file(tmpl, op.join(self.build_dir, 'index.html'))

    def write_readme_file(self):
        tmpl = '[{}](http://fontdirectory.github.io/collection/#/{}/)'.format(self.repo_slug, self.repo_slug)
        self.write_file(tmpl, op.join(self.build_dir, 'README.md'))

    def copy_ttf_fonts(self):
        pattern = '*.ttf'
        src_dir = os.path.abspath(self.build_dir)
        dst_dir = os.path.join(self.css_dir, 'fonts')
        fonts_files = [f for f in fnmatch.filter(os.listdir(src_dir), pattern)]
        for font_file in fonts_files:
            src = os.path.join(src_dir, font_file)
            print('Copying file: {} -> {}'.format(src, dst_dir))
            shutil.copy2(src, dst_dir)

    @lazy_property
    def version(self):
        return git_info(self.config)

    @lazy_property
    def repo(self):
        fontbakery_url = build_fontbakery_url()
        fontbakery_master = build_fontbakery_url('blob', 'master')
        fontbakery_edit_master = build_fontbakery_url('edit', 'master')
        fontbakery_tests_url = build_fontbakery_url('blob', 'master',
                                                    'bakery_lint', 'tests')
        fontbakery_tests_edit_url = build_fontbakery_url('edit', 'master',
                                                         'bakery_lint', 'tests')
        fontbakery = dict(repo_url=fontbakery_url,
                          master_url=fontbakery_master,
                          master_edit_url=fontbakery_edit_master,
                          tests_url=fontbakery_tests_url,
                          tests_edit_url=fontbakery_tests_edit_url)
        repo_url = build_repo_url()
        repo_gh_pages = build_repo_url('tree', 'gh-pages')
        return dict(url=repo_url, gh_pages=repo_gh_pages, fontbakery=fontbakery)
