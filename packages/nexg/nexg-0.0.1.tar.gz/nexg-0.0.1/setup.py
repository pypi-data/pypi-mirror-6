from setuptools import setup

setup(name='nexg',
      version='0.0.1',
      description='Next Generation Sequencing Analysis Suite',
      author='nickytong',
      author_email='ptong1@mdanderson.org',
      license='MIT',
      packages=['nexg'],
	  scripts=['bin/nexg'],
	  zip_safe=False)