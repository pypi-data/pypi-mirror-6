import os
from setuptools import setup, find_packages


def read_file(filename):
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except:
        return ''

setup(
    name="dashboardmods",
    version=__import__('dashboardmods').get_version().replace(' ', '-'),
    url='https://github.com/callowayproject/dashboardmods',
    author='Corey Oordt',
    author_email='coreyoordt@gmail.com',
    description='A collection of dashboard modules for django-admin-tools',
    long_description=read_file('README.rst'),
    packages=find_packages(),
    include_package_data=True,
    # package_data={'dashboardmods': [
    #     'templates/*.html',
    #     'templates/*/*.html',
    #     'templates/*/*/*.html',
    # ]},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
