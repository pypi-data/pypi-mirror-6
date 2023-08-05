from setuptools import setup, find_packages
import os

version = '1.4'

tests_require = [
    'Products.Silva [test]',
    ]

setup(name='Products.SilvaPoll',
      version=version,
      description="Poll for Silva",
      long_description=open(os.path.join("Products", "SilvaPoll", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "SilvaPoll", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
      keywords='poll silva zope2',
      author='Guido Wesdorp, Wim Boucquaert, Jasper Op De Coul',
      author_email='info@infrae.com',
      url='https://github.com/silvacms/Products.SilvaPoll',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'z3locales',
        'Products.Silva',
        'Products.Formulator',
        'Products.SilvaExternalSources',
        ],
      tests_require = tests_require,
      extras_require = {'test': tests_require,}
      )
