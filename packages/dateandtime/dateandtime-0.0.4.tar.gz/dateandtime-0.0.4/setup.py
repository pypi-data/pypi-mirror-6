"""dateandtime's setup.py."""


from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """Shim in pytest to be able to use it with setup.py test."""

    def finalize_options(self):
        """Stolen from http://pytest.org/latest/goodpractises.html."""

        TestCommand.finalize_options(self)
        self.test_args = (
            "-v -rf --cov-report term-missing --cov dateandtime"
        ).split()
        self.test_suite = True

    def run_tests(self):
        """Also shamelessly stolen."""

        # have to import here, outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        raise SystemExit(errno)


setup(
    name="dateandtime",
    version="0.0.4",
    author="Adam Talsma",
    author_email="adam@talsma.ca",
    packages=["dateandtime"],
    scripts=["bin/dateandtime"],
    url="https://github.com/a-tal/dateandtime",
    description="A silly little text calendar application for your terminal",
    long_description=(
        "Dateandtime can run multiple different calendaring formats, it will "
        "run forever in your shell after it launches. It is not a curses app. "
        "If you think of more calendar formats that you'd like supported, "
        "please open a GitHub issue."
    ),
    download_url="https://github.com/a-tal/dateandtime",
    install_requires=["ddate>=0.0.4"],
    tests_require=["pytest", "pytest-cov", "mock"],
    cmdclass={"test": PyTest},
    license="BSD",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
    ],
)
