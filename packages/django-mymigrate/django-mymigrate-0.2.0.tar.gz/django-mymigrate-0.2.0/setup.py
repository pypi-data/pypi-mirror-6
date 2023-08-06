import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mymigrate',
    version='0.2.0',
    packages=['mymigrate'],
    include_package_data=True,
    license='BSD License',
    description='django-mymigrate is a wrapper on south that allows to quickly migrate all project apps with one command.',
    long_description=README,
    url='https://github.com/hellpain/django-mymigrate',
    author='hellpain',
    author_email='urchenko88@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
