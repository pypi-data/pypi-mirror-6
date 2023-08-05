from distutils.core import setup
from applitools import VERSION

setup(
    name='eyes-selenium',
    version=VERSION,
    packages=['applitools', 'applitools.utils'],
    data_files=[('samples', ['samples/applitools.py'])],
    url='http://www.applitools.com',
    license='Apache License, Version 2.0',
    author='Applitools Team',
    author_email='team@applitools.com',
    description='Applitools Eyes SDK For Selenium Python WebDriver',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing"
    ],
    keywords='applitools eyes selenium',
    install_requires=[
        'setuptools',
        'requests>=2.1.0',
        'selenium>=2.39.0',
        'pytz>=2013.8',
        'jsonpickle>=0.6.1'
    ]
)
