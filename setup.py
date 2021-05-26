import setuptools
from setuptools import setup

# TODO - Autosetup of ~/.wxuas for keys

setup(name='dronelogbook',
      version='0.0.1',
      description='Package for interacting with the DroneLogBook APII',
      url='',
      author='Tyler Bell',
      author_email='tyler.bell@ou.edu',
      license='MIT',
      packages=setuptools.find_packages(),
      package_data={},
      install_requires=[
          'requests',
      ],
      entry_points="""
      [console_scripts]
      """,
      zip_safe=False)
