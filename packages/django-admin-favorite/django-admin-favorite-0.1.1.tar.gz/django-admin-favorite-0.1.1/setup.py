import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-admin-favorite',
    version='0.1.1',
    packages=['adfav'],
    include_package_data=True,
    license='MIT License',
    description='A simple Django app to add items to favorite in admin interface.',
    long_description=README,
    author='Mike Volkov',
    author_email='freylis2@gmail.com',
    url='https://bitbucket.org/freylis/django-admin-favorite',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = [
        'Django >= 1.4',
    ],
)