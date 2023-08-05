from distutils.core import setup
from applitools import VERSION

setup(
    name='eyes-selenium',
    version=VERSION,
    packages=['applitools', 'applitools.utils'],
    data_files=[('samples', ['samples/test_script.py', 'samples/appium_android_sample.py'])],
    url='http://www.applitools.com',
    license='Apache License, Version 2.0',
    author='Applitools Team',
    author_email='team@applitools.com',
    description='Applitools Eyes SDK For Selenium Python WebDriver',
    long_description="""\
    Applitools Eyes SDK For Selenium Python WebDriver.

    Sample scripts are available inside the distribution under the 'samples' directory.
    """,
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
        'jsonpickle>=0.6.1'
    ]
)
