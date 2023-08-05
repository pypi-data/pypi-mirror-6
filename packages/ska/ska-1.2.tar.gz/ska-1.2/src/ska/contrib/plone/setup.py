import os
from setuptools import setup, find_packages

try:
    readme = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
except:
    readme = ''

version = '1.1'

setup(
    name = 'ska.contrib.plone.ska',
    version = version,
    description = "Signing (HTTP) requests using symmetric-key algorithm.",
    long_description = readme,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords = 'signing (HTTP) requests, symmetric-key algorithm, signing URLs, python, plone',
    author = 'Artur Barseghyan',
    author_email = 'artur.barseghyan@gmail.com',
    url = 'https://github.com/barseghyanartur/ska/contrib/plone/ska/',
    license = 'GPL 2.0/LGPL 2.1',
    packages = find_packages('.'),
    package_dir = {'': '.'},
    namespace_packages = ['ska', ],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'setuptools',
        # -*- Extra requirements: -*-
    ],
    extras_require = {'test': ['plone.app.testing', 'robotsuite']},
    entry_points = """
        # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
    """,
)
