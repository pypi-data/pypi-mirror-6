from distutils.core import setup

setup(
    name='CallQueue',
    version='0.1.0',
    author="Joshua R. English",
    author_email="Joshua.R.English@gmail.com",
    packages=['queueable',],
    url="https://code.google.com/p/pycallqueue/",
    license='LICENSE.txt',
    description='Store functions and methods for delayed callback',
    long_description=open('README.txt').read(),
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development',
    ],
)