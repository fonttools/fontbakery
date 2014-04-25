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

from bakery.app import db


class User(db.Model):
    """
    User model, related to GitHub account.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(60), index=True)
    name = db.Column(db.String(200))
    avatar = db.Column(db.String(1000))
    email = db.Column(db.String(200))
    github_access_token = db.Column(db.String(200), nullable=False, index=True)

    def __init__(self, login):
        self.login = login

    @property
    def token(self):
        """ Return GitHub token. Used to sigh requests. """
        return self.github_access_token

    def getGithub(self):
        """ Return public link to GitHub user profile page """
        return "https://github.com/%s" % self.login

    @staticmethod
    def get_or_init(login):
        """ Find user with `login` in database if not then create new instance """
        user = User.query.filter_by(login=login).first()
        if user is None:
            user = User(login)
        return user
