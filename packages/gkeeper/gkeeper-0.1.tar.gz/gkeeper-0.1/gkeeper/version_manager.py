"""Revision management using git."""

from ConfigParser import DuplicateSectionError
from git import Repo
import os

KEEPER_NAME = 'gkeeper'
KEEPER_EMAIL = 'blah@blah.com'

class VersionManager(object):
    """Store versioned files in a git repository."""

    def __init__(self, path):
        """Initialize a git repo.

        Idempotent; will harmlessly reinitialize an existing repo.

        Args:
            path: Path on disk to the repository.
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path)
            self.repo = Repo.init(path)
            self.cf_writer = self.repo.config_writer()
            self.cf_writer.add_section('user')
            self.cf_writer.set('user', 'name', KEEPER_NAME)
            self.cf_writer.set('user', 'email', KEEPER_EMAIL)

        except DuplicateSectionError:
            pass

    def add_file(self, name):
        """Add a file."""
        self.repo.git.add(name)

    def commit(self, message):
        """Commit changes to already-added files."""
        self.repo.git.commit('-m %s' % message)
