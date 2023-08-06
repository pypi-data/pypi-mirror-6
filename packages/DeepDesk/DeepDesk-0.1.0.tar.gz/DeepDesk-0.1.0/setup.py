import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="DeepDesk",
    version = "0.1.0",
    packages = find_packages(),

    install_requires = [
            'password>=0.2',
            'isodate>=0.5',
            'pystemmer>=1.3.0',
            'requests>=2.2.1'
        ],
    author = "Domino Marama",
    author_email = "domino@dominodesigns.info",
    description = "Flexible data storage, with indexing, templates and validation",
    long_description = read('README'),
    keywords = "deepdesk json index validate storage database",
    url="https://bitbucket.org/Domino_Marama/deepdesk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.3",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Indexing",
    ],
)
