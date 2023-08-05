import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'django-multisessionform',
    version = '0.1',
    description = 'Allows users to complete a ModelForm over multiple sessions"',
    long_description = README,
    
    author = 'Chaim Kirby',
    author_email = 'chaimkirby@gmail.com',
    url = 'http://github.com/ckirby/django-multisessionform',
    license = 'BSD License', 
    
    packages=find_packages(),
    include_package_data = True,
    install_requires=['Django >=1.4'],
    
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)