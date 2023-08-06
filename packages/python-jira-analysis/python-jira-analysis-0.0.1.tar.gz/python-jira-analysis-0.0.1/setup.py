#!/usr/bin/env python
# limitations under the License.

'''JIRA tools.'''

__author__ = 'tomasz.kustrzynski@shazam.com'
__version__ = '0.0.1'

from setuptools import find_packages

# The base package metadata to be used by both distutils and setuptools
METADATA = dict(
    name="python-jira-analysis",
    version=__version__,
    packages=find_packages(),
    author='Shazam',
    author_email='tomasz.kustrzynski@shazam.com',
    description='JIRA dashboard tools for Kanban',
    license='Apache License 2.0',
    url='ssh://hg@bitbucket.org/fikander/python-jira-analysis',
    keywords='jira kanban',
)

# Extra package metadata to be used only if setuptools is installed
SETUPTOOLS_METADATA = dict(
    zip_safe=False,
    install_requires=[
        'setuptools',
        'django',
        'jira-python',
        'numpy',
        'pytz',
        'restkit',
        'gspread',
        'readline',
        'python-dateutil',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet',
    ],
    test_suite='tests.suite',
    scripts = [
        'scripts/jira_analysis_manage.py'
    ],
    data_files=[('etc', ['jira_analysis/settings.py'])],
)


def Read(file):
    return open(file).read()


def BuildLongDescription():
    return '\n'.join([Read('README.md'), Read('CHANGES')])


def Main():
    # Build the long_description from the README and CHANGES
    METADATA['long_description'] = BuildLongDescription()

    # Use setuptools if available, otherwise fallback and use distutils
    try:
        import setuptools
        METADATA.update(SETUPTOOLS_METADATA)
        setuptools.setup(**METADATA)
    except ImportError:
        import distutils.core
        distutils.core.setup(**METADATA)


if __name__ == '__main__':
    Main()
