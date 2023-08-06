from setuptools import setup, Command, find_packages
from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)

setup(
    name="jscov8",
    version="0.1.0",
    description="JavaScript coverage tool built with Python and V8.",
    author="Lex Berezhny",
    author_email="lex@damoti.com",
    url="http://github.com/damoti/jscov8",
    license="Apache Software License",
    platforms=["unix", "linux", "osx", "cygwin", "win32"],
    py_modules=["jscov8"],
    tests_require=['pytest'],
    cmdclass={"test": PyTest},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Utilities",
    ],
    keywords = "js javascript coverage pyv8 v8 pyjx",
)
