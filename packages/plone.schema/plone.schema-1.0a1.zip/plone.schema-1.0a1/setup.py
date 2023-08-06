from setuptools import setup, find_packages

version = '1.0a1'

setup(name='plone.schema',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
          "Framework :: Zope2",
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: BSD License",
      ],
      keywords='plone schema',
      author='',
      author_email='',
      url='https://github.com/plone/plone.schema',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.z3cform'
      ],
      extras_require={
          'test': ['plone.app.testing'],
      },
      )
