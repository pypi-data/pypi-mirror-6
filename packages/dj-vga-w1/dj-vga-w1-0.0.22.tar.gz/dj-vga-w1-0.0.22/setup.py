"""The deployment script.

The files and modules specified here mostly concern the `bdist_egg` command,
    and the .egg file

Relating the `sdist` command, the files to be included in the source
    distribution will be included as described in the `MANIFEST.mf`

"""
import os
import sys
from setuptools import setup, find_packages

current_dir = os.getcwd()
deployable_dir = os.path.join(os.getcwd(), 'dpl1_main')
sys.path = list(set(sys.path))
sys.path.remove(current_dir)
sys.path.append(deployable_dir)


def read(fname):
    """Returns the lines of the file given by `fname`

    :param fname:
    :return:
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


found_packages = find_packages()
setup(
    name="dj-vga-w1",
    version='0.0.22',
    author='Ardelean Vlad',
    author_email="vlad.ardelean@3pillarglobal.com",
    description=("The Django learning program project - a site where the uses"
                 "can take tests, and the admins can maintain configurations"
                 "for these tests"
    ),
    url='https://github.com/vladiibine/dlp-assignment1',
    keywords="example tutorial django",
    packages=found_packages,
    package_data={'': ['*.html', '*.sqlite3', '*.json', '*.css', '*.js']},
    long_description=read('README.txt'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: Free For Educational Use",
    ],
    install_requires=["django==1.6.1", "south==0.8.4"],
    include_package_data=True
)