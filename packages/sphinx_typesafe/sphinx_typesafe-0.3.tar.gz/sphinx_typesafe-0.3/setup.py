import os, re
from setuptools import setup, find_packages

name = 'sphinx_typesafe'

here = os.path.abspath(os.path.dirname(__file__))
init_file = os.path.join(here, name, '__init__.py')
version_re = "\s*__version__\s*=\s*((\"([^\"]|\\\\\")*\"|'([^']|\\\\')*'))"
version = re.search(version_re, open(init_file).read()).groups()[0][1:-1]

README  = open(os.path.join(here, 'README.rst')).read()
AUTHORS = open(os.path.join(here, 'AUTHORS.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

short_description = 'Type checking @typesafe employing Sphinx docstrings'
long_description = (
    README
    + '\n' +
    AUTHORS
    + '\n' +
    CHANGES
)

setup_requires = [
    'setuptools_git >= 0.3',
    ]

install_requires = [
    'zope.interface',
    ]

tests_require = [
    'pytest>=2.4.2',
    'pytest-cov',
    'pytest-pep8!=1.0.3',
    'pytest-xdist',
    ]

docs_require = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface',
    ]


setup(name=name,
      version=version,
      description=short_description,
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Pylons",
          "Framework :: Pyramid",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      author='Klaas',
      author_email='khz@tzi.org',
      maintainer='Richard Gomes',
      maintainer_email='rgomes.info@gmail.com',
      url='https://github.com/frgomes/' + name,
      keywords='type checking docstring',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      setup_requires=setup_requires,
      install_requires=install_requires,
      test_suite=name+'/tests',
      tests_require = tests_require,
      extras_require={
          'testing': tests_require,
          'docs': docs_require,
          },
      )
