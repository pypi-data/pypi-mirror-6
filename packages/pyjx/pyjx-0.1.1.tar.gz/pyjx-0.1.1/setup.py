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
    name="pyjx",
    version="0.1.1",
    description="Python to JavaScript translator and runtime.",
    author="Lex Berezhny",
    author_email="lex@damoti.com",
    url="http://pyjx.org",
    license="Apache Software License",
    platforms=["unix", "linux", "osx", "cygwin", "win32"],
    packages=find_packages(),
    include_package_data=True,
    tests_require=['pytest'],
    cmdclass={"test": PyTest},
    zip_safe=False,
    entry_points={"console_scripts":[
        "pyjampiler=pyjs.pyjampiler:pyjampiler",
        "pyjxcompile=pyjs.translator:main",
        "pyjxbuild=pyjs.browser:build_script",
        "pyv8run=pyjs.pyv8.pyv8run:main",
        "pyjxtest=pyjs.pyjstest:pyjstest"
    ]},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: Implementation",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Widget Sets",
        "Topic :: Utilities",
    ],
    keywords = "pyjx pyjs js javascript py2js python2js python2javascript",
)
