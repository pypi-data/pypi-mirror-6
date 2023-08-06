"""dateandtime's setup.py."""


from setuptools import setup


setup(
    name="dateandtime",
    version="0.0.3",
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
    tests_require=['nose'],
    test_suite='nose.collector',
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
