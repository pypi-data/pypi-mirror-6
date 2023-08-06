import sys
from setuptools import setup

__version__ = "0.0.2"

install_requires = [
    "docker-py==0.3.0",
    "gevent==1.0",
    "dnslib==0.8.3",
    "PyYAML==3.10"
]


if sys.version[:2] <= [2, 6]:
    install_requires.append('argparse==1.2.1')


setup(
    name="dockerns",
    description="Docker Service DNS Server",
    author="James Cunningham",
    author_email="tetrauk@gmail.com",
    url="https://github.com/jamescun/dockerns",
    licence="MIT",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: Name Service (DNS)"
    ],
    version=__version__,
    packages=["dockerns"],
    zip_safe=True,
    include_package_data=False,
    install_requires=install_requires,
    entry_points="""
[console_scripts]
dockerns = dockerns.cli:run
"""
)
