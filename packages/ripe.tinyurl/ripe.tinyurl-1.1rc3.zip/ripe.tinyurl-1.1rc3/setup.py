from setuptools import setup, find_packages

version = '1.1rc3'

setup(name='ripe.tinyurl',
      version=version,
      description="Short URL app for Plone",
      long_description=open("README.txt").read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          ],
      keywords='tinyurl',
      author='Adam Castle',
      author_email='acastle@ripe.net',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ripe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.testing',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      paster_plugins=["ZopeSkel"],
      )
