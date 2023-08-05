import os
import re
from setuptools import setup

VERSION = re.search(
    r"VERSION\s*=\s*['\"](.*)['\"]",
    open(os.path.join(os.path.dirname(__file__), 'simple_settings', '__init__.py')).read()
).group(1)

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-simple-settings',
    version=VERSION,
    packages=['simple_settings'],
    install_requires=['Django>=1.3'],
    include_package_data=True,
    license='MIT License',
    description='A very simple settings configurable in Django Admin Panel.',
    long_description=README,
    url='https://github.com/alikus/django-simple-settings',
    author='Albert Tugushev',
    author_email='albert@tugushev.ru',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
