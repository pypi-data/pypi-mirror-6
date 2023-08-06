# -*- coding: utf-8 -*-
##############################################################################
#
#  Agha, Another GitHub API
#  Copyright (C) 2014 MRDEV Software (<http://mrdev.com.ar>).
#
#  Author: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this programe.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

__version__ = '0.1.0'
__license__ = 'LGPL-3'

import requests
import json

api_url = 'https://api.github.com'

class GitHubApiError(Exception):
    """
    GitHubApi errors.
    """
    def __init__(self, response):
        try:
            self.message = response.reason
            self.status_code = response.status_code
        except AttributeError:
            self.message = response.json()

    def __str__(self):
        try:
            return "[%s] %s" % (self.status_code, self.message)
        except AttributeError:
            return self.message

class GitHubApi:
    """
    CRUD operations with GitHub API v3.
    """

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.auth = (self.user, self.password)

    def __get(self, url):
        r = requests.get(url, auth=self.auth)
        if r.status_code != 200:
            raise GitHubApiError(r)
        return r.json()

    def __post(self, url, parameters):
        r = requests.post(url, auth=self.auth, data=json.dumps(parameters))
        if r.status_code != 201:
            raise GitHubApiError(r)

    def __patch(self, url, parameters):
        r = requests.patch(url, auth=self.auth, data=json.dumps(parameters))
        if r.status_code != 200:
            raise GitHubApiError(r)

    def __delete(self, url):
        """
        Delete a repo.
        """
        r = requests.delete(url, auth=self.auth)
        if r.status_code != 204:
            raise GitHubApiError(r)

    def get_repos(self, user):
        """
        Get user repositories.
        """
        return self.__get('%s/users/%s/repos' % (api_url,user))

    def get_org_repos(self, org):
        """
        Get organization repositories.
        """
        return self.__get('%s/users/%s/repos' % (api_url,org))

    def get_repo(self, user, repo):
        """
        Get repository.
        """
        return self.__get('%s/repos/%s/%s' % (api_url,user,repo))

    def get_myrepo(self, repo):
        """
        Get repository.
        """
        return self.get_repo(self.user, repo)

    def get_myrepos(self):
        """
        Get user repositories.
        """
        return self.get_repos(self.user)

    def get_profile(self, user):
        """
        Get user profile information.
        """
        return self.__get('%s/users/%s' % (api_url,user))

    def get_myprofile(self):
        """
        Get user profile information.
        """
        return self.__get('%s/user' % api_url)

    def create_repo(self, parameters):
        """
        Create a user repo.
        :param parameters: See http://developer.github.com/v3/repos/#input
        """
        self.__post('%s/user/repos' % api_url, parameters)

    def create_org_repo(self, org, parameters):
        """
        Create a organization repo.
        :param parameters: See http://developer.github.com/v3/repos/#input
        """
        self.__post('%s/orgs/%s/repos' % (api_url,org), parameters)

    def delete_repo(self, owner, repo):
        """
        Delete a repo.
        """
        self.__delete('%s/repos/%s/%s' % (api_url,owner,repo))

    def delete_myrepo(self, repo):
        """
        Delete a user repo.
        """
        self.delete_repo(self.user, repo)

    def edit_org_repo(self, org, repo, parameters):
        """
        Edit a organization repo.
        :param parameters: See http://developer.github.com/v3/repos/#input-1
        """
        if 'name' not in parameters:
            parameters['name'] = repo
        self.__patch('%s/repos/%s/%s' % (api_url,org,repo), parameters)

    def edit_myrepo(self, repo, parameters):
        """
        Edit a organization repo.
        :param parameters: See http://developer.github.com/v3/repos/#input-1
        """
        self.edit_org_repo(self.user, repo, parameters)
