from setuptools import setup, find_packages

version = '0.2'

setup(
    name='django-moneybookers',
    version=version,
    url='https://github.com/gotlium/django-moneybookers',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Django>=1.4',
    ]
)
