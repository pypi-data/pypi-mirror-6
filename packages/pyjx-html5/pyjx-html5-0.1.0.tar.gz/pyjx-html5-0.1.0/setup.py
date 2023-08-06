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
    name="pyjx-html5",
    version="0.1.0",
    description="Access web browser APIs from Python.",
    author="Lex Berezhny",
    author_email="lex@damoti.com",
    url="http://pyjx.org",
    license="Apache Software License",
    platforms=["unix", "linux", "osx", "cygwin", "win32"],
    packages=find_packages(),
    include_package_data=True,
    tests_require=["pytest"],
    install_requires=["pyjx"],
    cmdclass={"test": PyTest},
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: Software Development :: Widget Sets",
    ],
    keywords = "pyjx javascript js html5 dom api browser",
)
