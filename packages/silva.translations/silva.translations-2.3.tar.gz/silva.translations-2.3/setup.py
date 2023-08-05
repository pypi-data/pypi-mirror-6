from setuptools import setup, find_packages
import os

version = '2.3'

setup(name='silva.translations',
      version=version,
      description="Translations files in many languages for the Silva CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='silva translations',
      author='Infrae',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/silva.translations',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['silva'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.i18nmessageid',
          'zope.i18n',
          ],
      )
