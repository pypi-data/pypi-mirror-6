from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
LICENSE = open(os.path.join(here, 'LICENSE.txt')).read()

requires = ['requests', 'watchdog', 'argparse']

setup(name='dwupload',
      version='0.1.3',
      description="Demandware upload file watcher. "
                  "Keeps your files in sync with your sandbox so you don't have to use Eclipse",
      long_description=README + '\n\n' + CHANGES,
      license=LICENSE,
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7"
          ],
      author='Charlie Choiniere',
      author_email='nek4life@gmail.com',
      url='',
      keywords='demandware',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='dwupload',
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      dwupload = dwupload:main
      """,
      )