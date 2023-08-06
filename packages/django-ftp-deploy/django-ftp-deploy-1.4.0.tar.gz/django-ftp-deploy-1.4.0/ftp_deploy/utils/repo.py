import pycurl
import json
import re

import core
from .curl import curl_connection
from .decorators import check
from ftp_deploy.conf import *


class repository_parser(object):

    def __init__(self, data, service):
        self.service = service
        self.data = data
        self.service_repo = service.repo_source

    def credentials(self):
        """return login details"""
        if self.service_repo == 'bb':
            return BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password']
        elif self.service_repo == 'gh':
            return GITHUB_SETTINGS['username'], GITHUB_SETTINGS['password']

    def check_branch(self):
        """check if payload branch match set branch"""
        if self.service_repo == 'bb':
            last_commit = len(self.data['commits']) - 1
            if self.data['commits'][last_commit]['branch'] == self.service.repo_branch:
                return True
        elif self.service_repo == 'gh':
            ref = self.data['ref'].split('/')
            if ref[2] == self.service.repo_branch:
                return True

        return False

    def deploy_email(self):
        """return email of deploy user"""

        if self.service_repo == 'bb':
            if self.data['user'] == 'Restore':
                return []
            try:
                curl = curl_connection(BITBUCKET_SETTINGS['username'], BITBUCKET_SETTINGS['password'])
                curl.authenticate()
                url = 'https://bitbucket.org/api/1.0/users/%s/emails' % self.data['user']
                context = json.loads(curl.perform(url))
                return [context[0]['email']]
            except Exception, e:
                return []
        elif self.service_repo == 'gh':
            if self.data['pusher']['name'] == 'Restore':
                return []
            return self.data['pusher']['email']

    def deploy_name(self):
        """ return username of deploy user"""
        if self.service_repo == 'bb':
            return self.data['user']
        elif self.service_repo == 'gh':
            return self.data['pusher']['name']


class repository_api(object):

    def __init__(self, service_repo):
        self.service_repo = service_repo
        self.curl_init()

    def curl_init(self):
        if self.service_repo == 'bb':
            self.username = BITBUCKET_SETTINGS['username']
            self.password = BITBUCKET_SETTINGS['password']
        elif self.service_repo == 'gh':
            self.username = GITHUB_SETTINGS['username']
            self.password = GITHUB_SETTINGS['password']

        self.curl = curl_connection(self.username, self.password)
        self.curl.authenticate()

    def repositories(self):
        """Load list of repositories from repository account"""

        if(self.service_repo == 'bb'):
            url = 'https://bitbucket.org/api/1.0/user/repositories'
        elif(self.service_repo == 'gh'):
            url = 'https://api.github.com/user/repos'

        context = self.curl.perform(url)
        return context

    def add_hook(self, service, request):
        """Add hook and change repo_hook flag for service"""

        if(self.service_repo == 'bb'):
            url = 'https://api.bitbucket.org/1.0/repositories/%s/%s/services/ ' % (self.username, service.repo_slug_name)
            post = 'type=POST&URL=%s%s' % (core.absolute_url(request).build(), service.hook_url())
        elif(self.service_repo == 'gh'):
            url = 'https://api.github.com/repos/%s/%s/hooks' % (self.username, service.repo_slug_name)

            data = {
                "name": 'web',
                "active": True,
                "config": {
                    "url": '%s%s' % (core.absolute_url(request).build(), service.hook_url()),
                }
            }

            post = json.dumps(data)

        service.repo_hook = True
        service.save()
        context = self.curl.perform_post(url, post)
        return context


class commits_parser(object):

    """Commit parser for list of commits. Take commits dictionary captured from payload"""

    def __init__(self, commits, service_repo):
        self.commits = commits
        self.service_repo = service_repo

    def commits_info(self):
        """Return commits details list in format [message,author,raw_node]"""
        output = list()
        if self.service_repo == 'bb':
            [output.append([commit['message'], commit['author'], commit['raw_node']]) for commit in reversed(self.commits)]
        elif self.service_repo == 'gh':
            [output.append([commit['message'], commit['author']['name'], commit['id']]) for commit in reversed(self.commits)]

        return output

    def email_list(self):
        """Return email list from raw_author, limited to unique emails"""
        output = list()

        if self.service_repo == 'bb':
            for commit in self.commits:
                email = re.search('%s(.*)%s' % ('<', '>'), commit['raw_author']).group(1)
                output.append(email) if email not in output else False
        elif self.service_repo == 'gh':
            for commit in self.commits:
                email = commit['author']['email']
                output.append(email) if email not in output else False

        return output

    def file_diff(self):
        """Return files list grouped by added, modified and removed. Respect order of commits"""
        added, removed, modified = list(), list(), list()

        if self.service_repo == 'bb':
            for commit in self.commits:
                for file in commit['files']:
                    if file['type'] == 'added':
                        added.append(file['file']) if file['file'] not in added else False
                        removed.remove(file['file']) if file['file'] in removed else False
                    elif file['type'] == 'modified':
                        modified.append(file['file']) if file['file'] not in modified and file['file'] not in added else False
                    elif file['type'] == 'removed':
                        removed.append(file['file']) if file['file'] not in removed + added else False
                        added.remove(file['file']) if file['file'] in added else False
                        modified.remove(file['file']) if file['file'] in modified else False

        elif self.service_repo == 'gh':
            for commit in self.commits:
                for file in commit['added']:
                    added.append(file) if file not in added else False
                    removed.remove(file) if file in removed else False
                for file in commit['modified']:
                    modified.append(file) if file not in modified and file not in added else False
                for file in commit['removed']:
                    removed.append(file) if file not in removed + added else False
                    added.remove(file) if file in added else False
                    modified.remove(file) if file in modified else False

        return added,  modified, removed

    def files_count(self):
        count = 0

        if self.service_repo == 'bb':
            for commit in self.commits:
                count += len(commit['files'])
        elif self.service_repo == 'gh':
            for commit in self.commits:
                count += len(commit['added']) + len(commit['modified']) + len(commit['removed'])

        return count


class bitbucket_check(curl_connection):

    """Bitbucket check class contain all checking points for bitbucket repository, return True if fail"""

    def __init__(self, username, password, service):
        super(bitbucket_check, self).__init__(username, password)
        self.service = service

    @check('Bitbucket')
    def check_authentication(self):
        self.authenticate()
        self.perform('https://bitbucket.org/api/1.0/user/repositories')
        if self.curl.getinfo(pycurl.HTTP_CODE) != 200:
            raise Exception("Login Fail")

    @check('Bitbucket')
    def check_repo_exist(self):
        self.authenticate()
        repos = json.loads(self.perform('https://bitbucket.org/api/1.0/user/repositories'))
        for repo in repos:
            if repo['slug'] == self.service.repo_slug_name:
                return False, ''
        raise Exception("Repository %s doesn't exist" % self.service.repo_slug_name)

    @check('Bitbucket')
    def check_branch_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/branches' % (self.username, self.service.repo_slug_name)
        branches = json.loads(self.perform(url))
        try:
            branches[self.service.repo_branch]
        except KeyError, e:
            raise Exception("Branch %s doesn't exist" % self.service.repo_branch)

    @check('Bitbucket')
    def check_hook_exist(self):
        self.authenticate()
        url = 'https://bitbucket.org/api/1.0/repositories/%s/%s/services' % (self.username, self.service.repo_slug_name)
        hooks = json.loads(self.perform(url))

        if type(hooks) == list:
            for hook in hooks:
                if len(hook['service']['fields']) > 0:
                    value = hook['service']['fields'][0]['value']
                    if value.find(str(self.service.hook_url())) != -1 and hook['service']['type'] == 'POST':
                        return False, ''
        raise Exception("Hook is not set up")

    def check_all(self):
        status = self.check_authentication()
        if status[0] == True:
            return status

        status = self.check_repo_exist()
        if status[0] == True:
            return status

        status = self.check_branch_exist()
        if status[0] == True:
            return status

        return False, ''


class github_check(curl_connection):

    """Bitbucket check class contain all checking points for bitbucket repository, return True if fail"""

    def __init__(self, username, password, service):
        super(github_check, self).__init__(username, password)
        self.service = service

    @check('Github')
    def check_authentication(self):
        self.authenticate()
        self.perform('https://api.github.com/user/repos')
        if self.curl.getinfo(pycurl.HTTP_CODE) != 200:
            raise Exception("Login Fail")

    @check('Github')
    def check_repo_exist(self):
        self.authenticate()
        repos = json.loads(self.perform('https://api.github.com/user/repos'))
        for repo in repos:
            if repo['name'] == self.service.repo_slug_name:
                return False, ''
        raise Exception("Repository %s doesn't exist" % self.service.repo_slug_name)

    @check('Github')
    def check_branch_exist(self):
        self.authenticate()
        url = 'https://api.github.com/repos/%s/%s/branches' % (self.username, self.service.repo_slug_name)
        branches = json.loads(self.perform(url))
        for branch in branches:
            if branch['name'] == self.service.repo_branch:
                return False, ''
        raise Exception("Branch %s doesn't exist" % self.service.repo_branch)

    @check('Github')
    def check_hook_exist(self):
        self.authenticate()
        url = 'https://api.github.com/repos/%s/%s/hooks' % (self.username, self.service.repo_slug_name)
        hooks = json.loads(self.perform(url))

        if type(hooks) == list:
            for hook in hooks:
                value = hook['config']['url']
                if value.find(str(self.service.hook_url())) != -1 and hook['name'] == "web":
                    return False, ''

        raise Exception("Hook is not set up")

    def check_all(self):
        status = self.check_authentication()
        if status[0] == True:
            return status

        status = self.check_repo_exist()
        if status[0] == True:
            return status

        status = self.check_branch_exist()
        if status[0] == True:
            return status

        return False, ''
