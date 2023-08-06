from distutils.core import setup

with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='flickrstock',
    version='0.2',
    description='Download stock photos from flickr',
    long_description=long_description,
    author='Omar Khan',
    author_email='omar@omarkhan.me',
    url='https://github.com/omarkhan/flickrstock',
    py_modules=['flickrstock'],
    scripts=['flickrstock'],
    requires=['flickrapi'],
)
