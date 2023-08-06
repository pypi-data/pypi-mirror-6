try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
        'name' : 'login_utils',
        'version' : '1.0.0',
        'author' : 'Kyle Roux',
        'author_email' : 'kyle@level2designs.com'
}
setup(**config)
