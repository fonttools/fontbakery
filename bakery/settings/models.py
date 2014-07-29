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
import datetime

from bakery.app import db
from bakery.json_field import JSONEncodedDict


class ProjectCache(db.Model):
    __tablename__ = 'project_cache'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    data = db.Column(JSONEncodedDict)
    updated = db.Column(db.DateTime(timezone=False), default=datetime.datetime)

    @classmethod
    def get_user_cache(cls, username):
        return ProjectCache.query.filter_by(login=username).first()

    @classmethod
    def refresh_repos(cls, repos, username):
        """ Stores repositories data received from github to database

            .. note::

            Each item in repos data is strongly formed and defined in github
            API documentation https://developer.github.com/v3/repos/#response
        """
        if not repos:
            return
        cache = ProjectCache.get_user_cache(username)
        if not cache:
            cache = ProjectCache()
            cache.login = username
        cache.data = repos
        # note the time
        cache.updated = datetime.datetime.utcnow()
        # add the cache to the database
        db.session.add(cache)
        db.session.commit()


class FontStats(db.Model):
    __tablename__ = 'font_stats'
    id = db.Column(db.Integer, primary_key=True)
    family = db.Column(db.String(60), index=True)
    total = db.Column(db.BigInteger())
    month = db.Column(db.BigInteger())
    week = db.Column(db.BigInteger())
    yesterday = db.Column(db.BigInteger())
    rate = db.Column(db.Float())

    @staticmethod
    def by_family(family):
        return FontStats.query.filter_by(family=family.lower()).first()


db.create_all()
