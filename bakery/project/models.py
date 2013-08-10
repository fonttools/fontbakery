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
from flask import current_app, json
from ..decorators import lazy_property
from ..extensions import db

from .state import (project_state_get, project_state_save)


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

    builds = db.relationship('ProjectBuild', backref='project', lazy='dynamic')

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
        _state, _local = project_state_get(project = self)
        return {'state': _state, 'local': _local}

    def save_state(self):
        project_state_save(self)

    def setup_status(self):
        # Return project status.
        return self.config['local'].get('source', None)

    def read_tree(self):
        return self.config['local']['tree']

    @property
    def title(self):
        # Can be changed when #142 is fixed
        if self.config['state'].get('familyname', None):
            return "%s (%s)" % (self.config['state']['familyname'], self.clone)
        else:
            return self.clone

    def asset_by_name(self, name):
        DATA_ROOT = current_app.config.get('DATA_ROOT')
        if name == 'log':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.process.log' % self)
        elif name == 'yaml':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.bakery.yaml' % self)
        elif name == 'metadata':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % self, 'METADATA.json')
        elif name == 'metadata_new':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % self, 'METADATA.json.new')
        elif name == 'license':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.in/' % self, self.config['state']['license_file'])
        elif name == 'description':
            fn = os.path.join(DATA_ROOT, '%(login)s/%(id)s.out/' % self, 'DESCRIPTION.en_us.html')
        else:
            fn = None
        return fn

    def read_asset(self, name = None):
        fn = self.asset_by_name(name)
        if os.path.exists(fn):
            return unicode(open(fn, 'r').read(), "utf8")
        else:
            return ''

    def save_asset(self, name = None, data = None, **kwarg):
        if name == 'description':
            f = open(self.asset_by_name(name), 'w')
            f.write(data)
            f.close()
        elif name == 'metadata':
            f = open(self.asset_by_name(name), 'w')
            json.dump(json.loads(data), f, indent=2, ensure_ascii=True) # same params as in generatemetadata.py
            f.close()

            if kwarg.get('del_new') and kwarg['del_new']:
                if os.path.exists(self.asset_by_name('metadata_new')):
                    os.remove(self.asset_by_name('metadata_new'))

    def __getitem__(self, key):
        # make magic mapping works
        return self.__dict__.get(key)

class ProjectBuild(db.Model):
    __tablename__ = 'project_build'
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    githash = db.Column(db.String(40))
    is_success = db.Column(db.Boolean())
