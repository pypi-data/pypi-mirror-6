import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

requires = [
    'pyramid >= 1.5a1',
    'deform',
    'pyramid_layout',
    'webhelpers',
    ]

setup(name='pyramid_backend',
      version='1.0',
      description='pyramid_backend',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Hoc .T Do',
      author_email='hoc3010@gmail.com',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='notification',
      install_requires=requires,
      )