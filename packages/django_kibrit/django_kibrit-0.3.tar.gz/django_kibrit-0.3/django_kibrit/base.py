import os
from subprocess import Popen, PIPE

from django.core.cache import cache

from django_kibrit.constants import DJANGO_KIBRIT_CACHED_KEY_ID


class GitRevision(object):
    """
    Return the 8 character long git revision number or an empty string
    """

    def __init__(self, path=None):
        """
        Get the cached tag for the cached key id. Otherwise create your own
        """
        self.path = path

    @property
    def revision(self):
        """
        Get current revision
        """
        revision = self.init_repo()
        cache.set(DJANGO_KIBRIT_CACHED_KEY_ID, revision, 60)
        return revision

    def init_repo(self):
        """
        The command to run and tag to return
        """
        try:
            return self.git('git describe --always --tags')
        except Exception, err:
            return ''

    def git(self, command=None):
        """
        Run a subprocess for the git command.
        """
        try:
            proc = Popen(command.split(), stderr=PIPE, stdout=PIPE, close_fds=(os.name == 'posix'), cwd=self.path)
        except Exception, err:
            return ''
        try:
            output, error= [s.strip() for s in proc.communicate()]
        except Exception, err:
            output = ''
        return output
