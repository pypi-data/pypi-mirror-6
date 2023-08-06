from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
# Courtesy of: https://pythonhosted.org/an_example_pypi_project/setuptools.html
import os
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# -------------------------
# Setup
# -------------------------
setup(name='repackage',
      version='0.2a',
      description= ("Repackaging, i.e. it intelligently adds directories to"
                    " the lib path. "
                    "Used either by modules moved into to a subdirectory "
                    "or to prepare the import of a non-registered package "
                    "(in any relative path)."),
      url='www.settlenext.com',
      author='Laurent Franceschetti',
      author_email='developer@settlenext.com',
      keywords ="package relative path module import library",
      license='MIT',
      packages=['repackage'],
      long_description=read('README'),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License"
      ],
      zip_safe=False)



