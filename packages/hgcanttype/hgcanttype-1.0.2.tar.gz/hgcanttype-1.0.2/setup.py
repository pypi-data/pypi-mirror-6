try:
    from setuptools import setup
except:
    from distutils.core import setup

requires = []
try:
    import mercurial
except ImportError:
    requires.append('mercurial')

setup(
    name='hgcanttype',
    version='1.0.2',
    author='Nathan Hoad',
    author_email='nathan@getoffmalawn.com',
    maintainer='Nathan Hoad',
    maintainer_email='nathan@getoffmalawn.com',
    url='http://bitbucket.org/getoffmalawn/hgcanttype',
    description='',
    long_description=open('README').read(),
    keywords='hg mercurial',
    license='GPLv2+',
    py_modules=['hgcanttype'],
    install_requires=requires,
)

