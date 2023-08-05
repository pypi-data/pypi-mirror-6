from setuptools import setup, find_packages
import os

name = 'izug.seantis.dir.events'
description = (
    "Integration of seantis.dir.events into izug."
)
version = '1.0rc1'


def get_long_description():
    readme = open('README.rst').read()
    history = open(os.path.join('docs', 'HISTORY.rst')).read()
    contributors = open(os.path.join('docs', 'CONTRIBUTORS.rst')).read()

    # cut the part before the description to avoid repetition on pypi
    readme = readme[readme.index(description) + len(description):]

    return '\n'.join((readme, contributors, history))


setup(name=name, version=version, description=description,
      long_description=get_long_description(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Seantis GmbH',
      author_email='info@seantis.ch',
      url='https://github.com/seantis/izug.seantis.dir.events',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['izug', 'izug.seantis', 'izug.seantis.dir'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'seantis.dir.events>=1.0rc1',
          'izug.basetheme',
          'collective.geo.zugmap',
          'plone.app.theming'
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
