"""
	hadoop-manager
	~~~~~

	Python wrapper around Hadoop streaming jar.
"""

from setuptools import setup


setup(name='hadoop-manager',
      version='0.0.1',
      author='Jure Ham',
      license='GPLv3',
      author_email='jure.ham@zemanta.com',
      description="Python wrapper for hadoop.",
      url='https://github.com/Zemanta/hadoop-manager',
      packages=['hdpmanager'],
      long_description=__doc__,
      platforms='any',
      zip_safe=True)
