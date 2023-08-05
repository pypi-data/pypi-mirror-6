from setuptools import setup, find_packages

setup(
    name='whitelist',
    version='0.2.8',
    packages=['whitelist'],
    install_requires=['django'],
    url = 'http://bitbucket.org/cent/whitelist/',
    license='GNU General Public License (GPL)',
    author='Vadim Statishin',
    author_email='statishin@gmail.com',
    description='Dynamic white list',
    keywords = 'django whitelist blacklist block access',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Security',
        'Topic :: System :: Logging',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
