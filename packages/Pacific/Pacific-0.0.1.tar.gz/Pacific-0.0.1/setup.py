import os

from setuptools import setup, find_packages


here = lambda path: os.path.join(os.path.abspath(os.path.dirname(__file__)), path)

with open(here('README.rst')) as f:
    README = f.read()

with open(here('CHANGES.txt')) as f:
    CHANGES = f.read()

with open(here('requirements.txt')) as f:
    rows = f.read().strip().split('\n')
    requires = []
    for row in rows:
        row = row.strip()
        if row and not (row.startswith('#') or row.startswith('http')):
            requires.append(row)


# Setup
# ----------------------------

setup(name='Pacific',
      version='0.0.1',
      description='Pacific',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Web Environment',
          'Framework :: Pyramid',
          'Intended Audience :: Developers',
          'License :: OSI Approved',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Operating System :: POSIX',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      ],
      author='Maxim Avanov',
      author_email='maxim.avanov@gmail.com',
      url='https://github.com/avanov/Pacific',
      keywords='web wsgi pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pacific',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main =pacific:main
      [console_scripts]

      [babel.extractors]
      plim = plim.adapters.babelplugin:extract
      """,
      )
