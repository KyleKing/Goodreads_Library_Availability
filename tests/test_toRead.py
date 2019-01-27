"""Test Goodreads To-Read functionality."""

from os import unlink, getcwd
from os.path import isfile, join
from shutil import copyfile

from gr_lib_sync.toRead import CONSUMER_KEY, CONSUMER_SECRET, clearCache, downloadGRShelf, envFn, loadEnv, updateEnv

# Adjust for relative directory
envBackupFn = '.env-backup.json'


def backupEnv():
    """Backup the environment file."""
    if isfile(envFn):
        if isfile(envBackupFn):
            unlink(envBackupFn)
        copyfile(envFn, envBackupFn)
    else:
        raise RuntimeError('Error: no envFile: {}'.format(join(getcwd(), envFn)))


def restoreEnv():
    """Restore the environment file."""
    if isfile(envFn):
        if isfile(envBackupFn):
            unlink(envFn)
            copyfile(envBackupFn, envFn)
        else:
            backupEnv()
    else:
        raise RuntimeError('Error: no envFile: {}'.format(join(getcwd(), envFn)))


def test_loadEnv():
    """Test that the minimum keys exist in the env."""
    backupEnv()
    env = loadEnv()
    assert CONSUMER_KEY in env
    assert CONSUMER_SECRET in env


# TODO: Add additional tests. Need to split downloadGRList into smaller functions
# FIXME: Create tests that run without a valid .env.json
