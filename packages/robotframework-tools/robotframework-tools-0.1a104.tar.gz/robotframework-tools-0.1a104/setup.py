import sys
from setuptools import setup
from pkg_resources import require, DistributionNotFound


VERSION = open('VERSION').read().strip()

REQUIRES = open('requirements.txt').read()


setup(
  name='robotframework-tools',
  version=VERSION,
  description=(
    'Python Tools for Robot Framework and Test Libraries.'
    ),
  author='Stefan Zimmermann',
  author_email='zimmermann.code@gmail.com',
  url='http://bitbucket.org/userzimmermann/robotframework-tools',

  license='GPLv3',

  install_requires=REQUIRES + (
    'robotframework >= 2.8' if sys.version_info[0] < 3
    else 'robotframework-python3 >= 2.8.3'
    ),
  packages=[
    'robottools',
    'robottools.library',
    'robottools.library.session',
    'robottools.library.context',
    'robottools.library.inspector',
    'robottools.testrobot',
    'robotshell',
    'robotshell.magic',
    ],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords=[
    'robottools', 'robot', 'framework', 'robotframework', 'tools',
    'test', 'automation', 'testautomation',
    'testlibrary', 'testcase', 'keyword', 'pybot',
    'robotshell', 'ipython',
    'python3',
    ],
  )
