import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

py_version = sys.version_info[:2]

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, "README.rst")).read()
    README += open(os.path.join(here, "HISTORY.rst")).read()
except IOError:
    README = "http://floqq.github.com/Rockefeller"

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name="Rockefeller",
      version="1.2.1",
      description="Money, currencies and exchange rates library.",
      long_description=README,
      author="ikame",
      author_email="anler86@gmail.com",
      url="http://floqq.github.com/Rockefeller/",
      license="MIT",
      install_requires=["six"],
      tests_require=["pytest", "mock"],
      cmdclass={"test": PyTest},
      keywords="money currency exchange rates",
      classifiers=[
          "Environment :: Plugins",
          "Environment :: Console",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Intended Audience :: Financial and Insurance Industry",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Office/Business :: Financial"])
