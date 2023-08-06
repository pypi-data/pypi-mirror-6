from setuptools import setup, find_packages
import os

version = '2.4'

setup(name='Products.FileSystemSite',
      version=version,
      description="Make available in ZODB file system resources in Zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("Products", "FileSystemSite", "HISTORY.txt")).read(),
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: Zope Public License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='file system site zope2',
      author='Zope community',
      author_email='info@infrae.com',
      url='https://github.com/infrae/Products.FileSystemSite',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Zope2',
          ],
      )
