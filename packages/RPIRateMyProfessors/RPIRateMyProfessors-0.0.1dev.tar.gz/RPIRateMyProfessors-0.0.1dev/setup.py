from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='RPIRateMyProfessors',
      version=version,
      description="some RPI RateMyProfessor functionality",
      long_description=("Some RateMyProfessor functionality, specific to RPI instructors. Retrieve difficulty or url of review page, given a professor's last name"),
      classifiers=[
        "Topic :: Utilities",
      ],
      keywords='RPI RateMyProfessors RPIRateMyProfessors',
      author='linksapprentice1',
      author_email='linksapprentice1@gmail.com',
      url='http://pythonhosted.org/RPIRateMyProfessors',
      license= 'MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      )
