from setuptools import setup, find_packages

# Dynamically calculate the version based on huron.VERSION.
version = __import__('huron').get_version()

with open('README.rst') as file:
  long_description = file.read()

setup(name='huron',
      version=version,
      url='https://bitbucket.org/tominardi/huron',
      description="Tools for Django websites",
      long_description=long_description,
      author='Thomas Durey',
      author_email='tominardi@gmail.com',
      license='BSD',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      platforms=["Linux"],
      )
