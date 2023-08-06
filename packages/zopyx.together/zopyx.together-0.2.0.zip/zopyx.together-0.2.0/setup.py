from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='zopyx.together',
      version=version,
      description="Plone integration with together.js",
      long_description=open("README.rst").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone TogetherJS',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://github.com/zopyx/zopyx.together',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zopyx', 'zopyx.together'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.i18nmessageid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
