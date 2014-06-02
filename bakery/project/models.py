# coding: utf-8
# Copyright 2013 The Font Bakery Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# See AUTHORS.txt for the list of Authors and LICENSE.txt for the License.

import os
import yaml
import magic
import lxml.etree as etree
import re
from datetime import datetime
import difflib

from flask import current_app
from blinker.base import lazy_property

from ..app import db
from ..utils import save_metadata
from ..tasks import (process_project, prun, project_git_sync,
                     upstream_revision_tests, result_tests,
                     generate_subsets_coverage_list)
from .state import project_state_get, project_state_save, walkWithoutGit


class Project(db.Model):
    __tablename__ = 'project'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    name = db.Column(db.String(60), index=True)
    full_name = db.Column(db.String(60))
    html_url = db.Column(db.String(60))
    data = db.Column(db.PickleType())
    clone = db.Column(db.String(400))
    is_github = db.Column(db.Boolean(), index=True)

    # `is_ready` means that project is waiting until project is synced and
    # upstream tests complete. it is very important to disable any user action
    # on project until all tests finish
    is_ready = db.Column(db.Boolean(), index=True, default=False)

    def cache_update(self, data):
        self.html_url = data['html_url']
        self.name = data['name']
        self.data = data

    @lazy_property
    def config(self):
        # if it is not purely visible, but @lazy_property decorator cache state
        # values in runtime, when this class property acessed for the 1st time
        # it store state value. You can access it and modify, but at the end of
        # the request all modifications dies if wasn't saved
        #
        _state, _local = project_state_get(project=self)
        return {'state': _state, 'local': _local}

    def save_state(self):
        project_state_save(self)

    def setup_status(self):
        # Return project status.
        return self.config['local'].get('source', None)

    @property
    def source_files_type(self):
        if self.config['state'].get('source_files_type'):
            return self.config['state']['source_files_type']
        else:
            if self.config['local']['ufo_dirs']:
                return 'ufo'
            elif self.config['local']['ttx_files']:
                return 'ttx'
            else:
                return None

    @property
    def title(self):
        """
        Return project title, resolved from repo clone if no rename family name given
        """
        # Split the git clone URL on /, take the last part, remove '.git' if it exists
        # eg "https://github.com/davelab6/league-gothic.git" -> league-gothic.git -> league-gothic
        title = self.clone.split('/')[-1].replace('.git', '')
        # If URL terminates with a /, title will be None, so take the 2nd to last part
        # eg "https://github.com/davelab6/league-gothic/" -> league-gothic
        if not title:
            title = self.clone.split('/')[-2].replace('.git', '')
        # use the family rename input if it was given
        if self.is_ready and self.config['state'].get('familyname', None):
            title = self.config['state']['familyname']
        return title

    def read_asset(self, name=None):
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        if name == 'yaml':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % self)
        elif name == 'license':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self, self.config['state']['license_file'])
        else:
            return ''

        if os.path.exists(fn) and os.path.isfile(fn):
            return unicode(open(fn, 'r').read(), "utf8")
        else:
            return ''

    def treeFromFilesystem(self, folder=None):
        """
        Read files tree in specied directory

        :param folder: handle for tree, either 'in' or 'out'

        Returns:
            folderContents: Dictionary of file and directory strings
        """
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        _out = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % self)
        if folder == 'in' and os.path.exists(_in):
            folderContents = walkWithoutGit(_in)
        elif folder == 'out' and os.path.exists(_out):
            folderContents = walkWithoutGit(_out)
        else:
            folderContents = {'Sorry, filesystem unavailable': ''}
        return folderContents

    def textFiles(self):
        """
        Read all the text files found in the _in repo

        Returns:
            textFiles: Dictionary of file and directory strings
        """
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        textFiles = {}
        for textFile in self.config['local']['txt_files']:
            fn = os.path.join(_in, textFile)
            if os.path.exists(fn) and os.path.isfile(fn):
                textFiles[textFile] = unicode(open(fn, 'r').read(), "utf8")
        return textFiles

    def revision_tree(self, revision):
        """ Get specific revision files as tree in format supported
            by tree macros """
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        d = {}
        for file in prun("git ls-tree --name-only -r %(revision)s" % locals(), cwd=_in).splitlines():
            level = d
            for part in file.split("/"):
                if part not in level:
                    level[part] = {}
                level = level[part]

        return d

    def revision_file(self, revision, fn):
        """ Read specific file from revision """
        # XXX: [xen] need review here, not sure that it is 100% safe
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        fn = fn.replace('"', '')
        # XXX: result can be tree
        data = prun('git show "%(revision)s:%(fn)s"' % locals(), cwd=_in)
        mime = magic.from_buffer(data, mime=True)
        if mime.startswith("text"):
            data = unicode(data, "utf8")
        return mime, data

    def revision_info(self, revision):
        """ Return revision info for selected git commit """
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        return prun("git show --quiet --format=short %(revision)s" % locals(), cwd=_in).decode('utf-8')

    def revision_tests(self, revision='HEAD'):
        # XXX: check revision for safety
        if revision == 'HEAD':
            return upstream_revision_tests(self, self.current_revision())
        else:
            return upstream_revision_tests(self, revision)

    def passed_tests_files(self, revision='HEAD'):
        passed = []
        for name, td in self.revision_tests(revision).items():
            if td.get('passed', False):
                passed.append(name)

        return passed

    @property
    def family_stat(self):
        from ..models import FontStats

        # stats_family_name have hihger priority
        fn = self.config['state'].get('stats_family_name') or self.config['state'].get('familyname')

        if fn:
            return FontStats.by_family(fn)

    def __getitem__(self, key):
        """ Magic method that allow to access ORM properties using
        object-dot-propertyname """
        # make magic mapping works
        return self.__dict__.get(key)

    def __len__(self):
        return len(self.__dict__.keys())

    def current_revision(self):
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        return prun("git rev-parse --short HEAD", cwd=_in).strip()

    def get_subsets(self):
        return sorted(generate_subsets_coverage_list(self))

    def sync(self):
        """ Call in background git syncronization """
        project_git_sync.delay(self)

    def gitlog(self, skip=0):
        """ Return list of dictionaries described first 101 git repo commits

            Each dictionary contains `hash` (str[:7]), `date`, `message`
            (first line of git message), `author`."""
        from git import Repo

        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        repo = Repo(_in)

        commits = repo.iter_commits('HEAD', max_count=101, skip=skip)
        result = []
        for commit in commits:
            result.append({
                'hash': commit.hexsha[:7],
                'date': datetime.fromtimestamp(commit.committed_date),
                'message': commit.summary,
                'author': u'%s <%s>' % (commit.author.name,
                                        commit.author.email)
            })

        return result

    def diff_files(self, left, right):
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        data = prun("""git diff %(left)s %(right)s""" % locals(), cwd=_in)
        data = data.decode('utf-8').encode('ascii', 'xmlcharrefreplace')
        file_diff = {}
        t = []
        current_file = None
        source_start = target_start = 0
        RE_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))?\ @@[ ]?(.*)")

        def unpack(source_start, source_len, target_start, target_len, section_header):
            return int(source_start), int(target_start)

        data_lines = data.splitlines()
        data_lines.append(' ')
        for l in data_lines:
            if l.startswith('diff --git'):
                if current_file:
                    file_diff[current_file] = "\n".join(t)
                current_file = l[14 + (len(l[11:]) - 1) / 2:]
                t = []
                continue
            elif l.startswith('index'):
                continue
            elif l.startswith('---'):
                continue
            elif l.startswith('+++'):
                continue
            elif l.startswith('new file'):
                continue

            l = l.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")
            first = l[0]
            last = l[1:]
            l = l.rstrip(" \t\n\r")
            if l.startswith('Binary files'):
                l = '<tr><td></td><td></td><td><span class="text-center">Binary file not shown</span></td></tr>'
            elif first == '@':
                re_hunk_header = RE_HUNK_HEADER.match(l)
                if re_hunk_header:
                    hunk_info = re_hunk_header.groups()
                    source_start, target_start = unpack(*hunk_info)
                l = "<tr class='hunk'><td></td><td></td><td><pre>%s<pre></td></tr>" % (l)
            elif first == "+":
                target_start = target_start + 1
                l = "<tr class='ins'><td></td><td class='num'>%s</td><td><pre>%s</pre></td></tr>" % (target_start, last)
            elif first == "-":
                source_start = source_start + 1
                l = "<tr class='del'><td class='num'>%s</td><td></td><td class='del'><pre>%s</pre></td></tr>" % (source_start, last)
            else:
                target_start = target_start + 1
                source_start = source_start + 1
                l = "<tr><td class='num'>%s</td><td class='num'>%s</td><td><pre>%s<pre></td></tr>" % (source_start, target_start, l)

            t.append(l)

        if current_file:
            file_diff[current_file] = "\n".join(t)

        return file_diff

    def diff_files_slow(self, left, right):
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        _in = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self)
        names = prun("""git diff --name-only %(left)s %(right)s""" % locals(), cwd=_in)
        data = prun("""git diff %(left)s %(right)s""" % locals(), cwd=_in)
        file_diff = {}
        # list of known xml file extensions
        xml_ext = ['.svg', '.ttx', '.plist', '.glif', '.xml']
        for f in names.splitlines():
            param = {'left': left, 'right': right, 'name': f}
            #file_diff[f] = prun("""git diff %(left)s %(right)s -- "%(name)s" """ % param, cwd=_in)
            if os.path.splitext(f)[1] in xml_ext:
                left_content = prun("""git show %(left)s:"%(name)s" """ % param, cwd=_in)
                right_content = prun("""git show %(right)s:"%(name)s" """ % param, cwd=_in)

                if left_content.startswith('fatal:'):
                    left_content = ''
                if right_content.startswith('fatal:'):
                    right_content = ''
                # left
                try:
                    left_xml = etree.tostring(etree.fromstring(left_content), pretty_print=True)
                except etree.XMLSyntaxError:
                    # if returned data is not real xml
                    left_xml = left_content
                # right
                try:
                    right_xml = etree.tostring(etree.fromstring(right_content), pretty_print=True)
                except etree.XMLSyntaxError:
                    # if returned data is not real xml
                    right_xml = right_content

                file_diff[f] = "".join([x for x in difflib.unified_diff(left_xml, right_xml, fromfile="a/" + f, tofile="b/" + f, lineterm='')])

            else:
                file_diff[f] = prun("""git diff %(left)s %(right)s -- "%(name)s" """ % param, cwd=_in)

        for f in file_diff.keys():
            text = file_diff[f]
            text = text.replace("&", "&amp;").replace(">", "&gt;").replace("<", "&lt;")
            t = []
            for l in text.splitlines():
                if l[0] == '+':
                    l = "<ins>%s</ins>" % l
                elif l[0] == "-":
                    l = "<del>%s</del>" % l
                elif l[0] == "^":
                    l = "<ins>%s</ins>" % l
                t.append(l.rstrip(" \t\n\r"))

            file_diff[f] = "\n".join(t)

        return file_diff


class ProjectBuild(db.Model):
    __tablename__ = 'project_build'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    project = db.relationship(Project)
    # git rev-parse --short HEAD
    revision = db.Column(db.String(40))
    is_done = db.Column(db.Boolean(), default=False)
    created = db.Column(db.DateTime, default=datetime.now)
    modified = db.Column(db.Boolean(), default=False)
    updated = db.Column(db.DateTime, default=datetime.now, onupdate=db.func.now())

    @staticmethod
    def make_build(project, revision, force_sync=False):
        """ Initiate project build process

        :param project: `Project` instance
        :param revision: git revision id
        :return: `ProjectBuild` instance
        """
        if revision == 'HEAD':
            revision = project.current_revision()
        build = ProjectBuild(project=project, revision=revision)
        db.session.add(build)
        db.session.commit()
        db.session.refresh(project)
        db.session.refresh(build)
        if current_app.config.get('BACKGROUND'):
            process_project.delay(project, build, revision, force_sync)
        else:
            process_project(project, build, revision, force_sync)
        return build

    @property
    def path(self):
        param = self.get_path_params()
        return '%(root)s/%(login)s/%(id)s.out/%(build)s.%(revision)s/' % param

    def metadata_exists(self):
        """ Return True if build has METADATA.json """
        param = self.get_path_params()
        filepath = self.asset_list['metadata'] % param
        return os.path.exists(filepath) and os.path.isfile(filepath)

    def description_exists(self):
        """ Return True if build has DESCRIPTION.en_us.html """
        param = self.get_path_params()
        filepath = self.asset_list['description'] % param
        return os.path.exists(filepath) and os.path.isfile(filepath)

    def result_tests_finished(self):
        """ Return True if build completely executed and appropriate yaml
            file exists """
        param = self.get_path_params()
        yamlpath = ('%(root)s/%(login)s/%(id)s.out/'
                    '%(build)s.%(revision)s.rtests.yaml') % param
        return os.path.exists(yamlpath) and os.path.isfile(yamlpath)

    def read_rtests_data(self):
        param = self.get_path_params()
        yamlpath = ('%(root)s/%(login)s/%(id)s.out/'
                    '%(build)s.%(revision)s.rtests.yaml') % param
        try:
            test_data = yaml.load(open(yamlpath).read())
        except (IOError, yaml.YAMLError):
            return {}

        success = []
        failure = []
        error = []
        for k, tests in test_data.items():
            error += tests.get('error', [])
            success += tests.get('success', [])
            failure += tests.get('failure', [])
        return {'success': success, 'error': error, 'failure': failure}

    def read_upstream_tests_data(self):
        """ Return summary of upstream tests """
        test_data = self.utests()
        success = []
        failure = []
        error = []
        for k, tests in test_data.items():
            error += tests.get('error', [])
            success += tests.get('success', [])
            failure += tests.get('failure', [])
        return {'success': success, 'error': error, 'failure': failure}

    def utests(self):
        """ Return saved upstream test data """
        if not self.is_done:
            return {}

        param = self.get_path_params()
        _out_yaml = '%(root)s/%(login)s/%(id)s.out/utests/%(revision)s.yaml' % param
        try:
            return yaml.load(open(_out_yaml).read())
        except (IOError, yaml.YAMLError):
            return {}

    def read_links404_test_data(self):
        """ Return saved DESCRIPTION.en_us.html test data. """
        param = self.get_path_params()
        _out_yaml = '%(root)s/%(login)s/%(id)s.out/%(build)s.%(revision)s.404links.yaml' % param
        return yaml.load(open(_out_yaml).read())

    asset_list = {
        'description': '%(root)s/%(login)s/%(id)s.out/%(build)s.%(revision)s/DESCRIPTION.en_us.html',
        'metadata': '%(root)s/%(login)s/%(id)s.out/%(build)s.%(revision)s/METADATA.json',
        'metadata_new': '%(root)s/%(login)s/%(id)s.out/%(build)s.%(revision)s/METADATA.json.new',
    }

    def get_path_params(self):
        return {'login': self.project.login, 'id': self.project.id,
                'revision': self.revision, 'build': self.id,
                'root': current_app.config.get('DATA_ROOT')}

    def read_asset(self, name=None):
        param = self.get_path_params()

        fn = self.asset_list[name] % param
        if os.path.exists(fn) and os.path.isfile(fn):
            return unicode(open(fn, 'r').read(), "utf8")
        else:
            return ''

    def save_asset(self, name=None, data=None, **kwarg):
        """ Save static files into out folder """
        param = self.get_path_params()

        if name == 'description':
            f = open(self.asset_list['description'] % param, 'w')
            f.write(data)
            f.close()
        elif name == 'metadata':
            save_metadata(data, self.asset_list['metadata'] % param)

            if kwarg.get('del_new') and kwarg['del_new']:
                if os.path.exists(self.asset_list['metadata_new'] % param):
                    os.remove(self.asset_list['metadata_new'] % param)

        self.modified = True
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)

    def files(self):
        return walkWithoutGit(self.path)

    def result_tests(self):
        return result_tests(self.project, self, )
