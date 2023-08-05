import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

version = '0.3'

setup(
    name = "unweb.recipe.uwsgi",
    version = version,
    description = """\
            This is a recipe to build a uwsgi binary as well as the xml config file.
            It's a modified version of https://github.com/psychotechnik/eqb.recipe.uwsgi
            which is in turn a modified version of 
            https://github.com/shaunsephton/shaunsephton.recipe.uwsgi
    """,
    long_description=README + '\n\n' +  CHANGES,    
    classifiers=[
    'Framework :: Buildout',
    'Topic :: Software Development :: Build Tools',
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    ],      
    #package_dir={'': 'eqb/recipe/uwsgi'},
    packages=find_packages(),
    keywords='buildout, uwsgi',
    author='Dimitris Moraitis',
    author_email='dimo@unweb.me',
    url='https://github.com/unweb/unweb.recipe.uwsgi',
    license='BSD',
    zip_safe=False,
    install_requires=[
        'zc.buildout',
        'zc.recipe.egg',
        'PasteDeploy',
    ],
    entry_points = {
        'zc.buildout': ['default = unweb.recipe.uwsgi:UWSGI']
    },
    )
