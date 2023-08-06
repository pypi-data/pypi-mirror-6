
with open('README.txt') as f:
    long_description = f.read()

from distutils.core import setup
setup(
    name = "nomit",
    packages = ["nomit"],
    version = "1.0",
    description = "Process Monit HTTP/XML",
    author = "Markus Juenemann",
    author_email = "markus@juenemann.net",
    url = "https://github.com/mjuenema/nomit",
    download_url = "https://github.com/mjuenema/nomit/tarball/1.0",
    keywords = ["xml", "Monit", "MMonit"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        ],
    long_description = long_description
)
