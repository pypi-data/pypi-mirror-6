from setuptools import setup, find_packages

version = '3.0.3.1'

tests_require = [
    'plone.app.testing',
    'pyquery'
    ]

setup(name='tomcom.plone.bootstrap',
      version=version,
      description='bootstrap for plone',
      long_description=open("README.rst").read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='font awesome',
      author='tomcom GmbH',
      author_email='mailto:info@tomcom.de',
      url='https://github.com/tomcom-de/tomcom.plone.bootstrap',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['tomcom','tomcom.plone'],
      include_package_data=True,
      install_requires=[
        'setuptools',
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