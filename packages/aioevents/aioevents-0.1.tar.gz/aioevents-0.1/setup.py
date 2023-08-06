from distutils.core import setup

def read_file(name):
    """
    Read file content
    """
    f = open(name)
    try:
        return f.read()
    except IOError:
        print("could not read %r" % name)
        f.close()


setup(
    name='aioevents',
    version='0.1',
    author='Jamie Bliss',
    author_email='astronouth7303@gmail.com',
    url='https://github.com/astronouth7303/aioevents',
    packages=['aioevents',],
    license='MIT License',
#    long_description=...,
    install_requires=['asyncio'],
    provides=['aioevents'],
    classifiers=[ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
