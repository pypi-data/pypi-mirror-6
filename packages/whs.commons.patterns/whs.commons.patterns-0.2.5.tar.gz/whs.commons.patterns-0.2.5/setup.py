from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup

TOP_LEVEL_NAME = "whs"

setup(name=TOP_LEVEL_NAME+'.commons.patterns',
      version='0.2.5',
      description='Common patterns usable in any context',
      long_description='''WHS Ltd provides collection of pure-python modules.

This is patterns package, containing some a few standard design pattern
implementation.

Most credit for singleton class goes to Duncan Booth.
''',
      maintainer = "Filip Malczak",
      maintainer_email='filip(dot)malczak(at)gmail(dot)com',
      url='devzone.itadmin.pl',
      namespace_packages=[
          TOP_LEVEL_NAME,
      ],
      packages=[
          TOP_LEVEL_NAME+'.commons.patterns'
      ],
      py_modules=[
          "ez_setup"
      ],
      license = "BSD license (http://opensource.org/licenses/bsd-license.php); "
      "owner: Web Harvesting Solutions Ltd;"
      "year: 2013",
      platforms =[ "Any"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Utilities"
      ],
     )
