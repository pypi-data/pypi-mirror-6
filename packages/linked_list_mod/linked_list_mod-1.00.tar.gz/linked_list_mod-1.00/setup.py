
from setuptools import setup, find_packages
setup(
    name = "linked_list_mod",
    version = "1.00",
    packages = find_packages(),
    scripts = ['linked_list_mod.py'],

    # metadata for upload to PyPI
    author = "Daniel Richard Stromberg",
    author_email = "strombrg@gmail.com",
    description='Pure Python linked list module',
    long_description='''
A pure python linked list class is provided.  It is
thoroughly unit tested, passes pylint, and is known
to run on CPython 2.7, CPython 3.3, Pypy 2.2 and
Jython 2.7b1.
''',
    license = "Apache v2",
    keywords = "linked list",
	 url='http://stromberg.dnsalias.org/~strombrg/linked-list',
	 platforms='Cross platform',
	 classifiers=[
		 "Development Status :: 5 - Production/Stable",
		 "Intended Audience :: Developers",
		 "Programming Language :: Python :: 2",
		 "Programming Language :: Python :: 3",
		 ],
)

