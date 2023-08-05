import os
import shutil
from setuptools import setup, find_packages

version = '0.2'

name='openid-selector'

here = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'README.txt')).read()
AUTHORS = open(os.path.join(here, 'AUTHORS.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

long_description = (
    README
    + '\n' +
    AUTHORS
    + '\n' +
    CHANGES
)


# define contents of staging area
pkg = name.replace('-','_')
entries = \
         [ ('js',     'js',     [ 'jquery-1.2.6.min.js', 'openid-en.js', 'openid-jquery.js' ]), \
           ('css',    'css',    [ 'openid.css', 'openid-shadow.css' ]), \
           ('images', 'images', [ 'openid-inputicon.gif', 'openid-providers-en.png' ]) ]

# create staging area
if not os.path.exists(pkg):
    os.mkdir(pkg)
    open('/'.join([pkg, '__init__.py']), 'a').close()
    for entry in entries:
        (from_dir, to_dir, files) = entry
        os.mkdir('/'.join([pkg, to_dir]))
        open('/'.join([pkg, to_dir, '__init__.py']), 'a').close()
        for file in files:
            src = '/'.join([from_dir, file])
            dst = '/'.join([pkg, to_dir, file])
            shutil.copyfile(src, dst)
 

setup(name=name,
      version=version,
      description= name + " is a frontend in JavaScript for authentication with OpenID, OAuth2, etc",
      long_description=long_description,
      classifiers=[
          "Programming Language :: JavaScript",
          "Topic :: Internet :: WWW/HTTP",
      ],
      keywords='authentication frontend javascript openid oauth2',
      author='Richard Gomes',
      author_email='rgomes.info@gmail.com',
      url='http://' + name + '.readthedocs.org',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      setup_requires=[ 'setuptools-git' ],
      )
