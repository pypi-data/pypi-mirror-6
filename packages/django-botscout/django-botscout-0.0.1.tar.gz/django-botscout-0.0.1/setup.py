import os

from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-botscout',
    version='0.0.1',
    author='Joey Wilhelm',
    author_email='tarkatronic@gmail.com',
    license='License :: OSI Approved',
    long_description=README,
    url='http://labs.lyrical.net/lyrical/django-botscout',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django'
    ],
)