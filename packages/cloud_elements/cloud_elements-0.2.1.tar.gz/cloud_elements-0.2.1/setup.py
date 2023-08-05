from setuptools import setup, find_packages

setup(
    name='cloud_elements',
    version='0.2.1',
    author='Christian Rodriguez',
    author_email='christian.etpr10@gmail.com',
    packages=find_packages(),
    description='Cloud Elements Connector for Python',
    long_description='Cloud Elements Connector for Python',
    install_requires=[
        'requests'
    ],
    url='https://github.com/cloud-elements/elements-connector-python.git'
)