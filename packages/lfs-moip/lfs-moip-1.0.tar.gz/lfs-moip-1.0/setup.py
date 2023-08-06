from setuptools import setup, find_packages
import os

version = '1.0'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

setup(
    name='lfs-moip',
    version=version,
    description='Integration of MoIP into LFS',
    long_description=README,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='django e-commerce online-shop moip',
    author='Alan Justino da Silva',
    author_email='alan.justino@yahoo.com.br',
    url='https://github.com/alanjds/lfs-moip',
    download_url='https://github.com/alanjds/lfs-moip/tarball/'+version,
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'django-moip',
        'furl',
    ],
)
