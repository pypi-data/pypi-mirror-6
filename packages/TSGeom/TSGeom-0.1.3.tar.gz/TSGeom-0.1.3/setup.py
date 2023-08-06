from distutils.core import setup

setup(
    name='TSGeom',
    version='0.1.3',
    packages=['tsgeom'],
    license='BSD-new license',
    description='Python package for computing simple geometries on TS data.',
    long_description=open('README.txt').read(),
    author='John Bjorn Nelson',
    author_email='jbn@pathdependent.com',
    url='https://github.com/jbn/TSGeom',
    install_requires=[
        'numpy >= 1.8.0'
    ],
)
