from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup


TOP_LEVEL_NAME = "whs"

setup(name=TOP_LEVEL_NAME+'.utils.flask',
      version='0.2.0',
      description='Some Flask utils, targeting REST services',
      long_description='''WHS Ltd provides collection of pure-python modules.

This is package contatining some Flask utilities, created for easier REST
services implementation.
It provides Flask enhancment for creating classes for single applications, and
mixin for Flask-based classes allowing resource usage.
''',
      maintainer = "Filip Malczak",
      maintainer_email='filip(dot)malczak(at)gmail(dot)com',
      url='https://devzone.itadmin.pl',
      namespace_packages=[
          TOP_LEVEL_NAME,
      ],
      packages=[
          TOP_LEVEL_NAME+'.utils.flask'
      ],
      py_modules=[
          "ez_setup"
      ],
      install_requires=["whs.commons.abc", "flask"],
      license = "BSD license (http://opensource.org/licenses/bsd-license.php); "
      "owner: Web Harvesting Solutions Ltd; "
      "year: 2013",
      platforms =[ "Any"],
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Framework :: Flask",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: BSD License",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Utilities"
      ],
     )
