from setuptools import setup, find_packages
import sys, os

import pyul

kw = {}
if sys.version_info >= (3,):
    kw['use_2to3'] = True

setup(name=pyul.__name__,
      version=pyul.__version__,
      author=pyul.__author__,
      author_email=pyul.__author_email__,
      url=pyul.__url__,
      description=pyul.__description__,
      long_description=open('README.md').read(),
      license=open('LICENSE').read(),
      install_requires=open('requirements.txt').read().splitlines(),
      tests_require=open('test_requirements.txt').read().splitlines(),
      setup_requires=[],      
      keywords='',
      packages=find_packages(),
      namespace_packages=[],
      zip_safe=False,
      test_suite='nose.collector',
      entry_points="""[console_scripts]
      pyul = pyul.cli.main:main
      """,
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.4',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.0',
                   'Programming Language :: Python :: 3.1',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Software Development :: Testing',
                   ],
      **kw)
