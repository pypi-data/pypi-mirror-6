from setuptools import setup, find_packages
import os

version = '0.6'

setup(name='collective.zoomit',
      version=version,
      description="Integration of Zoom.it hosted image zoom in plone.",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Deepzoom Zoom.it Images Plone',
      author='Alec Mitchell, Jazkarta, Inc',
      author_email='alecpm@gmail.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""[z3c.autoinclude.plugin]
target = plone
      """,
      )
