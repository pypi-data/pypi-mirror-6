try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
try:
    from versionup import get_version
except ImportError:
    def get_version():
        return '1.0.0'


version = get_version()

config = {
    'name' : 'versionup',
    'version': version,
    'author': 'kyle roux',
    'author_email' : 'jstacoder@gmail.com',
    'description' : 'version update / management utility',
    'long_description': open('README','r').read(),
    'install_requires' : ['argparse'],
    'entry_points':{'console_scripts':
    ['upversion = versionup.command:main',
    'showversion = versionup:show_version']},
        }
setup(**config)
