from setuptools import setup, find_packages

PROJECT = "htmldiff"
VERSION = "0.1"

with open('README.md') as f:
    README = f.read()

with open('LICENSE.txt') as f:
    LICENSE = f.read()
	
setup(
    name=PROJECT,
    version=VERSION,
    author = "Ian Bicking <ian@ianbicking.org>, Richard Cyganiak <richard@cyganiak.de>, Ed Summers <ehs@pobox.com>, David Miro <lite.3engine@gmail.com>",
	description = "Outputs HTML that shows the differences in text between two versions of an HTML document.",
    long_description=README,
    license=LICENSE,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        ],
	py_modules=['htmldiff'],
    entry_points = {
        'console_scripts': ['htmldiff = htmldiff:main']
        },
    platforms=['Any']
    )
