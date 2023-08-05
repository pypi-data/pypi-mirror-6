from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup


TOP_LEVEL_NAME = "whs"

setup(name=TOP_LEVEL_NAME+'.commons.abc',
      version='0.7.0',
      description='Abstract base classes for enterprise and business usage',
      long_description='''WHS Ltd provides collection of pure-python modules.

This is ABC package, containing some base classes for (de)serialization, type
registration and session managment.
''',
      author='WHS Ltd',
      maintainer = "Filip Malczak",
      maintainer_email='filip(dot)malczak(at)gmail(dot)com',
      url='https://devzone.itadmin.pl',
      namespace_packages=[
          TOP_LEVEL_NAME,
      ],
      packages=[
          TOP_LEVEL_NAME+'.commons.abc'
      ],
      py_modules=[
          "ez_setup"
      ],
      install_requires = ["whs.commons.patterns"],
      license = "BSD license (http://opensource.org/licenses/bsd-license.php); "
      "owner: Web Harvesting Solutions Ltd; "
      "year: 2013",
      platforms =[ "Any"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Utilities"
      ],
     )
