from setuptools import setup

VERSION = '2.1.3'

setup(
    name="FerrisNose",
    version=VERSION,
    author='Jon Parrott',
    author_email='jjramone13@gmail.com',
    maintainer='Jon Parrott',
    maintainer_email='jjramone13@gmail.com',
    description='Nose plugin for testing Google App Engine application. Designed for the Ferris Framework but should work for any App Engine app.',
    url='https://bitbucket.org/jonparrott/ferrisnose',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],
    entry_points={
        'nose.plugins.0.10': [
            'ferris = ferrisnose.plugin:FerrisNose'
        ]
    },
    packages=['ferrisnose'],
    install_requires=[
        'nose>=1.3.0',
        'google-api-python-client>=1.2.0',
        'oauth2client>=1.2.0',
        'webtest',
        'protobuf>=2.4.0',
        'protorpc>=0.9.0',
    ],
)
