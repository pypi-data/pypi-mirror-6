import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires = [
    'pyramid>=1.3',
    ]

setup(name='pyramid_versionbadge',
      version='0.2',
      description=('A tween which renders a badge on '
                   'the page indicating the version.'),
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: Repoze Public License",
        ],
      keywords='wsgi pylons pyramid staging production testing',
      author=("Daniel Havlik",),
      author_email="dh@gocept.com",
      url="http://www.gocept.com",
      license="BSD",
      packages=find_packages(),
      zip_safe=False,
      install_requires=install_requires,
      entry_points='',
      )
