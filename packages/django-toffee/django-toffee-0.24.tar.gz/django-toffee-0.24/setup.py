import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-toffee',
    version='0.24',
    packages=['toffee'],
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to layout your applications.',
    long_description=README,
    url='http://www.bingorabbit.com/',
    author='Ibrahim Abdel Fattah Mohamed',
    author_email='bingorabbit@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django-bootstrap3',
        'django-eztables',
        'django-form-utils',
    ],
)
