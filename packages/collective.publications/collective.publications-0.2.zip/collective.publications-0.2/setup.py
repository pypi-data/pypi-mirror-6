from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='collective.publications',
      version=version,
      description="Provides a publication content type based on dexterity",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='plone content publications dexterity',
      author='Emmanuelle HELLY',
      author_email='emmanuelle.helly@makina-corpus.net',
      url='https://github.com/numahell/collective.publications/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'setuptools',
            'five.grok',
            'plone.app.dexterity',
            'plone.namedfile [blobs]',
            'collective.dexteritytextindexer',
            'collective.z3cform.widgets',
            'collective.z3cform.keywordwidget',
            'collective.z3cform.datetimewidget',
            'plone.app.referenceablebehavior',
            # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],

      )
