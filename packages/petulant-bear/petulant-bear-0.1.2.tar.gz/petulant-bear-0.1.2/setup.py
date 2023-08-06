try:
    from setuptools import setup, find_packages
    packages = find_packages()
except ImportError:
    from distutils import setup

setup(
    name='petulant-bear',
    version='0.1.2',
    description='Presents etree interface to netcdf4-python objects using NCML data model',
    author='David Stuebe',
    author_email='DStuebe@ASAScience.com',
    url='https://github.com/ioos/petulant-bear',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
    ],
    license='GPLv3',
    keywords='netcdf lxml xml metadata ncml',
    packages= ['petulantbear'],
    install_requires = [
            'netCDF4>=1.0.0',
            'nose>=1.2.0',
            'numpy>=1.7.0',
            'lxml>=3.2.1',
            ],
)
