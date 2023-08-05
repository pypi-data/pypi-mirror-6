# Copyright (c) 2013, Matt Layman
'''
Follow MarkWiki development on `GitHub
<https://github.com/mblayman/markwiki>`_. Developer documentation is on
`Read the Docs <https://markwiki.readthedocs.org/>`_.
'''

from setuptools import find_packages, setup

__version__ = '1.3'

# The docs import setup.py for the version so only call setup when not behaving
# as a module.
if __name__ == '__main__':
    with open('docs/releases.rst', 'r') as f:
        releases = f.read()

    long_description = __doc__ + '\n\n' + releases

    setup(
        name='MarkWiki',
        version=__version__,
        url='https://github.com/mblayman/markwiki',
        license='BSD',
        author='Matt Layman',
        author_email='matthewlayman@gmail.com',
        description='A simple wiki using Markdown',
        long_description=long_description,
        packages=find_packages(),
        entry_points={
            'console_scripts': ['markwiki = markwiki.server:run']
        },
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'argparse',
            'Flask',
            'Flask-Login',
            'Flask-WTF',
            'Frozen-Flask',
            'Markdown',
            'Pygments',
            'Whoosh',
        ],
        setup_requires=[
            'coverage',
            'nose'
        ],
        test_suite='markwiki.tests'
    )
