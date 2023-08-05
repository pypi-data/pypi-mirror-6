from setuptools import setup, find_packages
import os

version = '0.1.0'

long_description = (
    open('README.rst').read()
    + '\n' +
    open(os.path.join('docs', 'CHANGES.rst')).read()
    + '\n')

setup(name='pmr.wfctrl',
      version=version,
      description="Workflow controller",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://github.com/PMR/pmr.wfctrl',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['pmr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
