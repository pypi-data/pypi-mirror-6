from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse

from braces.views import JSONResponseMixin, LoginRequiredMixin

from ftp_deploy.conf import *
from ftp_deploy.models import Service
from ftp_deploy.utils.curl import curl_connection
from ftp_deploy.utils.core import absolute_url


class BitbucketAPIView(LoginRequiredMixin, JSONResponseMixin, SingleObjectMixin, View):

    """View for managing BitBucket API"""

    model = Service

    def dispatch(self, request, *args, **kwargs):
        self.bitbucket_username = BITBUCKET_SETTINGS['username']
        self.bitbucket_password = BITBUCKET_SETTINGS['password']
        return super(BitbucketAPIView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        curl = curl_connection(self.bitbucket_username, self.bitbucket_password)
        curl.authenticate()

        url = 'https://api.bitbucket.org/1.0/repositories'
        post = 'name=project_name&is_private=True'
        context = curl.perform_post(url, post)

        curl.close()

        return HttpResponse(context)

    def post(self, request, *args, **kwargs):
        try:

            curl = curl_connection(self.bitbucket_username, self.bitbucket_password)
            curl.authenticate()
            post = str()

            if self.request.POST['data'] == 'respositories':
                context = self.repositories(curl)
            elif self.request.POST['data'] == 'addhook':
                context = self.add_hook(curl, request)

            return self.render_json_response(context)

        finally:
            curl.close()

        return HttpResponse()

    def repositories(self, curl):
        """Load list of repositories from bitbucket account"""

        url = 'https://bitbucket.org/api/1.0/user/repositories'
        context = curl.perform(url)
        return context

    def add_hook(self, curl, request):
        """Add hook and change repo_hook flag for service"""

        service = self.get_object()
        url = 'https://api.bitbucket.org/1.0/repositories/%s/%s/services/ ' % (self.bitbucket_username, self.get_object().repo_slug_name)
        post = 'type=POST&URL=%s%s' % (absolute_url(request).build(), service.hook_url())
        service.repo_hook = True
        service.save()
        context = curl.perform_post(url, post)
        return context

    def add_respository(self, curl):
        """Add respository to repository account"""

        url = 'https://api.bitbucket.org/1.0/repositories'
        post = 'name=project_name'
        context = curl.perform_post(url, post)
        return context
