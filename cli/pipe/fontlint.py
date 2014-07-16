import os.path as op
import yaml

from checker import run_set
from checker.base import BakeryTestCase
from cli.system import stdoutlog


class FontLint(object):

    def __init__(self, project_root, builddir, stdout_pipe=stdoutlog):
        self.project_root = project_root
        self.builddir = builddir
        self.stdout_pipe = stdout_pipe

    def execute(self, pipedata):
        self.stdout_pipe.write('Run tests for baked files\n', prefix='### ')
        _out_yaml = op.join(self.builddir, '.tests.yaml')

        if op.exists(_out_yaml):
            return yaml.safe_load(open(_out_yaml, 'r'))

        result = {}
        for font in pipedata['bin_files']:
            result[font] = run_set(op.join(self.builddir, font), 'result',
                                   log=self.stdout_pipe)

        path = op.join(self.builddir, 'METADATA.json')
        result['METADATA.json'] = run_set(path, 'metadata',
                                          log=self.stdout_pipe)

        if not result:
            return

        l = open(_out_yaml, 'w')
        l.write(yaml.safe_dump(result))
        l.close()


# register yaml serializer for tests result objects.
def repr_testcase(dumper, data):

    def method_doc(doc):
        if doc is None:
            return "None"
        else:
            try:
                doc = ' '.join(doc.split())
                return doc.decode('utf-8', 'ignore')
            except:
                return ''

    try:
        err_msg = getattr(data, '_err_msg', '').decode('utf-8', 'ignore')
    except:
        err_msg = ''

    _ = {
        'methodDoc': method_doc(data._testMethodDoc),
        'tool': data.tool,
        'name': data.name,
        'methodName': data._testMethodName,
        'targets': data.targets,
        'tags': getattr(data, data._testMethodName).tags,
        'err_msg': err_msg
    }
    return dumper.represent_mapping(u'tag:yaml.org,2002:map', _)

yaml.SafeDumper.add_multi_representer(BakeryTestCase, repr_testcase)
