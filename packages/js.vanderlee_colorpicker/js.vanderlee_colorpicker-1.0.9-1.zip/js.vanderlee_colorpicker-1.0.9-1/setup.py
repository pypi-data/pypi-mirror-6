from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.0.9-1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('js', 'vanderlee_colorpicker', 'test_colorpicker.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.vanderlee_colorpicker',
    version=version,
    description="Fanstatic packaging of vanderlee/colorpicker",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='gocept Developers',
    author_email='mail@gocept.com',
    license='BSD',
    packages=find_packages(),namespace_packages=['js'],
    include_package_data=True,
    url='https://bitbucket.org/gocept/js.vanderlee_colorpicker',
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'js.jquery >= 1.7.1',
        'js.jqueryui >= 1.8.0',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'colorpicker = js.vanderlee_colorpicker:library',
            ],
        },
    )
