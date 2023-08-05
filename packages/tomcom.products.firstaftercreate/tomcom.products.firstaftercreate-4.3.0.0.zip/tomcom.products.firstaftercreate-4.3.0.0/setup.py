from setuptools import setup, find_packages

version = '4.3.0.0'

tests_require = [
    'plone.app.testing',
    'pyquery'
    ]

setup(name='tomcom.products.firstaftercreate',
      version=version,
      description='',
      long_description=open("README.rst").read(),
      classifiers=[
        'Framework :: Plone',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='tomcom plone',
      author='tomcom GmbH',
      author_email='mailto:info@tomcom.de',
      url='http://stash.tomcom.de/scm/PLONE/tomcom.products.firstaftercreate.git',
      license='GPL2',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.products'],
      include_package_data=True,
      install_requires=[
        'setuptools',
        'tomcom.tpcheck',
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require,
                     ),
      zip_safe=False,
      entry_points='''
[z3c.autoinclude.plugin]
target = plone
''',
)