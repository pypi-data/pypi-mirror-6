from setuptools import setup, find_packages

setup(
    name='cloud_elements',
    version='0.2',
    author='Christian Rodriguez',
    author_email='christian.etpr10@gmail.com',
    packages=find_packages(),
    description='Cloud elements api client for Python',
    long_description='Cloud elements api client for Python',
    install_requires=[
        'requests'
    ],
    download_url='https://github.com/chrisrodz/cloud-elements-python/tarball/0.1',
    url='https://github.com/chrisrodz/cloud-elements-python/'
)