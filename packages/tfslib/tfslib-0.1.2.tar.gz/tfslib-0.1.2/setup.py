from setuptools import setup

setup(
    name='tfslib',
    version='0.1.2',
    author='Volodymyr Buell',
    author_email='vbuell@gmail.com',
    url='https://bitbucket.org/volodymyr_buell/python-tfs',
    description=("Python client for Microsoft TFS issue tracker."),
    license='APL2',
    install_requires='suds',
    keywords='TFS tracker issue python client',
    py_modules=['tfslib'],
    #    test_suite = "tests",
    long_description='Provides functions for reading and updating Microsoft TFS items.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
