from setuptools import setup, find_packages

version = '0.1.1'
requires = [
    'pyramid==1.4.5'
]

setup(name='pyramid_webapp_scaffold',
      version=version,
      description="Pyramid Webapp Scaffold",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='pyramid scaffold webapp',
      author='Larry Weya',
      author_email='larryweya@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      entry_points="""\
      [pyramid.scaffold]
      webapp=pyramid_webapp_scaffold.scaffolds:WebAppTemplate
      """
      )
