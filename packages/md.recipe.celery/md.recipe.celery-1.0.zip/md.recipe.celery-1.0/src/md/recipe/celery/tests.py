import os
import sys
import tempfile
import shutil
import distutils
from doctest import ELLIPSIS, NORMALIZE_WHITESPACE, REPORT_UDIFF
from doctest import DocFileSuite
import doctest

from zc.buildout.testing import (
    buildoutTearDown, install_develop, normalize_path, bdist_egg, system)
from zc.buildout.tests import easy_install_SetUp
from zope.testing import renormalizing

# We want to ignore entire lines
doctest.ELLIPSIS_MARKER = '***'

# XXX more elegant way of going up in dir structure?
TEST_HARNESS = os.path.abspath(
    os.path.join(
        __file__, '..', '..', '..', '..', '..', 'test_harness'))


def setUp(test):
    easy_install_SetUp(test)
    create_celery_egg(test)
    install_develop('md.recipe.celery', test)

# This file needs to be generated since we want to change version number
SETUP_PY = """
from setuptools import setup
setup(
    name='celery', packages=['celery', 'celery.loaders'],
    entry_points={{'console_scripts': ['celeryd = celery:main',
    'celeryctl = celery:main']}}, zip_safe=True, version='{version}')
"""


def create_celery_egg(test):
    """Create a dummy celery egg for testing.
       The included scripts simply print the content of the celeryconfig
       module.
    """
    from zc.buildout.testing import write

    dest = test.globs['sample_eggs']
    tmp = tempfile.mkdtemp()
    try:
        # Copy all files/directories _inside_ TEST_HARNESS to tmp
        distutils.dir_util.copy_tree(TEST_HARNESS, tmp)
        write(tmp, 'setup.py', SETUP_PY.format(version='2.3.1'))
        bdist_egg(tmp, sys.executable, dest)

        # Create another celery egg with a different version for testing
        # updating the celery egg.
        write(tmp, 'setup.py', SETUP_PY.format(version='2.3.0'))
        bdist_egg(tmp, sys.executable, dest)
    finally:
        shutil.rmtree(tmp)


def test_suite():
    return DocFileSuite(
        'README.md',
        setUp=setUp, tearDown=buildoutTearDown,
        optionflags=ELLIPSIS | NORMALIZE_WHITESPACE | REPORT_UDIFF,
        checker=renormalizing.RENormalizing([normalize_path]),)
