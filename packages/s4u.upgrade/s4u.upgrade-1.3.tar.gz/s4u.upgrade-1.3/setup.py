import sys
from setuptools import setup
from setuptools import find_packages

version = '1.3'

install_requires = [
    'setuptools',
    'venusian',
    ]

if sys.version_info < (2, 7):
    install_requires.append('argparse')

setup(name='s4u.upgrade',
      version=version,
      description='2Style4You upgrade framework',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      author='Simplon B.V. - Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='https://readthedocs.org/builds/s4uupgrade/',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      namespace_packages=['s4u'],
      zip_safe=True,
      install_requires=install_requires,
      tests_require=['mock'],
      extras_require={'docs': ['sphinx'],
                      'tests': ['mock']},
      test_suite='s4u.upgrade',
      entry_points='''
      [console_scripts]
      upgrade = s4u.upgrade:upgrade
      ''')
