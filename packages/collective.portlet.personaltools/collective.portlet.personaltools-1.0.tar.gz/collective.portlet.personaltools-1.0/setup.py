from setuptools import setup, find_packages
import os

version = open("collective/portlet/personaltools/version.txt").read()

setup(name='collective.portlet.personaltools',
      version=version,
      description="Plone personal tools portlet",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='portlet personal tools',
      author='Bogdan Girman',
      author_email='bogdan.girman@gmail.com',
      url='https://github.com/collective/collective.portlet.personaltools',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
