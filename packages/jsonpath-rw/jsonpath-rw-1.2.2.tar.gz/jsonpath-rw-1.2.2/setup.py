import setuptools 
import io
import sys
import os.path
import subprocess

VERSION_PATH='jsonpath_rw/VERSION'

# Ensure that the VERSION file is shipped with the distribution
if 'sdist' in sys.argv:
    import jsonpath_rw.version
    with io.open(VERSION_PATH, 'w', encoding='ascii') as fh:
        fh.write(jsonpath_rw.version.git_version())

# This requires either jsonpath_rw/VERSION or to be in a git clone (as does the package in general)
# This is identical to code in jsonpath_rw.version. It would be nice to re-use but importing requires all deps
def stored_version():
    if os.path.exists(VERSION_PATH):
        with io.open(VERSION_PATH, encoding='ascii') as fh:
            return fh.read().strip()
    else:
        return None

def git_version():
    described_version_bytes = subprocess.Popen(['git', 'describe'], stdout=subprocess.PIPE).communicate()[0].strip()
    return described_version_bytes.decode('ascii')

version = stored_version() or git_version()

setuptools.setup(
    name='jsonpath-rw',
    version=version,
    description='A robust and significantly extended implementation of JSONPath for Python, with a clear AST for metaprogramming.',
    author='Kenneth Knowles',
    author_email='kenn.knowles@gmail.com',
    url='https://github.com/kennknowles/python-jsonpath-rw',
    license='Apache 2.0',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    packages = ['jsonpath_rw'],
    package_data = {'': ['VERSION']},
    test_suite = 'tests',
    install_requires = [ 'ply', 'decorator', 'six' ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
)
