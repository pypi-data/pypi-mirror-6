from distutils.core import setup

setup(name="Dieroller",
    version="2.1.0",
    author = 'Joshua R. English',
    author_email = 'Joshua.R.English@gmail.com',
    url = 'https://code.google.com/p/pydieroller',
    packages=['dieroller'],
    description = 'polyhedral die roller for games',
    long_description = '''Rolls polyhedral dice for games.
    Can handle mutliple dice and adjustments
    ''',
    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Role-Playing'
    ],
    )