from distutils.core import setup

setup(
    name = "fortune3py",
    version = "2.0.1",
    description = "Fortune cookies for Python3",
    author = "Jimmy Bahuleyan",
    author_email = "jimmy.bahuleyan@gmail.com",
    url = "https://github.com/jbahuleyan/fortune3py",
    scripts = ["fortune.py"],
    classifiers = ["Topic :: Games/Entertainment :: Fortune Cookies", "Programming Language :: Python :: 3", "License :: OSI Approved :: Apache Software License", "Operating System :: OS Independent"],
    requires = "argparse"
)
