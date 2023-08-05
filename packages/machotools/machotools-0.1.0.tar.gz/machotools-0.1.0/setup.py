import os.path as op

from setuptools import setup

VERSION = "0.1.0"

if __name__ == "__main__":
    with open(op.join("machotools", "__version.py"), "wt") as fp:
        fp.write("__version__ = '{0}'".format(VERSION))

    setup(name="machotools",
          version=VERSION,
          author="David Cournapeau",
          author_email="cournape@gmail.com",
          license="BSD",
          packages=["machotools", "machotools.tests"],
          install_requires=["macholib"],
          classifiers=[
              "Programming Language :: Python :: 2.6",
              "Programming Language :: Python :: 2.7",
              "Programming Language :: Python :: 3.2",
              "Programming Language :: Python :: 3.3",
          ])
