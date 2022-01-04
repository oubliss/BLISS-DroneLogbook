import setuptools
import os
import json
from setuptools import setup

# Configure the API key
configure = input("Would you like to configure your DroneLogBook API key? [y/n] ")

if configure.lower() == 'y':
    api_key = input("Please input your API Key: ")

    wxuas_dir = os.path.join(os.path.expanduser("~"), ".wxuas")
    if not os.path.exists(wxuas_dir):
        os.makedirs(wxuas_dir)

    with open(os.path.join(wxuas_dir, 'keys_test'), 'w') as fh:
        fh.write(json.dumps({'dlb_api_key': api_key, "dlb_url": "https://ou.dronelogbook.com"}, sort_keys=True, indent=4))


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
