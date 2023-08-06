#!/usr/bin/env python
import os

name = 'wither'
path = 'wither'


## Automatically determine project version ##
from setuptools import setup, find_packages
try:
    from hgdistver import get_version
except ImportError:
    def get_version():
        d = {}
        
        # handle single file modules
        if os.path.isdir(path):
            module_path = os.path.join(path, '__init__.py')
        else:
            module_path = path
            
        with open(module_path) as f:
            try:
                exec(f.read(), None, d)
            except:
                pass
            
        f.close
        return d.get("__version__", 0.1)

## Use py.test for "setup.py test" command ##
from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        pytest.main(self.test_args)

## Try and extract a long description ##
for readme_name in ("README", "README.rst", "README.md"):
    try:
        readme = open(readme_name).read()
    except (OSError, IOError):
        continue
    else:
        break
else:
    readme = ""

## Finally call setup ##
setup(
    name = name,
    version = get_version(),
    packages = [path],
    author = "Da_Blitz",
    author_email = "code@pocketnix.org",
    maintainer=None,
    maintainer_email=None,
    description = "XML Generation DSL",
    long_description = readme,
    license = "MIT BSD",
    keywords = "XML HTML Generation DSL",
    download_url=None,
    classifiers=None,
    platforms=None,
    url = "http://code.pocketnix.org/wither",
    zip_safe = True,
    setup_requires = ['hgdistver'],
    install_requires = ['distribute', 'lxml'],
    tests_require = ['pytest'],
    cmdclass = {'test': PyTest},
)
