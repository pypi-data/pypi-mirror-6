import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

description = ("A simple django plugin for sending push notifications"
               " from django server to sockjs clients")

setup(
    name="djazator",
    version="0.2.5",
    author="Mike Oskin",
    author_email="cheap.grayhat@gmail.com",
    description=description,
    license="MIT",
    keywords="django zeromq tornado sockjs",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
    },
    entry_points={
        'console_scripts': [
            'djazator-server = djazator.server:main',
            'djazator-mq = djazator.mq:main',
        ],
    },
    install_requires=['pyzmq >=2.0.0, <=2.2.0.1',
                      'sockjs-tornado==1.0.0',
                      'tornado==2.4.1'],
    long_description=read('README.rst'),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Framework :: Django"
    ],
)
