import os
from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.txt')) as f:
    README = f.read()



setup(
    name = "multipserve",
    version = "1.0.3",
    author = "Mario Idival",
    author_email = "marioidival@gmail.com",
    description = ("Script for using with multiples applications Pyramid"),
    long_description = README,
    license = "BSD",
    keywords = "multipserve pyramid threading",
    url = "https://github.com/marioidival/multi_pserve",
    scripts = ['multipserve/bin/multipserver.py'],
    packages=['multipserve'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Framework :: Pyramid",
        "Operating System :: Unix",
    ],
)
