from setuptools import setup, find_packages

setup(
    name='{project.name}',
    version='1.0.0',
    packages=find_packages(exclude=['test-data']),
    # author='YOUR NAME',
    # author_email='YOUR EMAIL',
    entry_points={{
        'sbgsdk.wrappers': [{wrappers}]
    }},
    install_requires=['sbgsdk=={project.version}', 'nose', 'path.py==4.1']
)
