from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

classifiers = [
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 2",
]

setup(name='trakio',
      version=version,
      description="Client library for accessing the trak.io API.",
      long_description="""\
Client library for making calls to the trak.io API.""",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        ].extend(classifiers),
      keywords=["user analytics", "user engagement", "trak.io"],
      author='Robin Orheden',
      author_email='robin.orheden@userapp.io',
      url='https://github.com/userapp-io/trakio-python/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
