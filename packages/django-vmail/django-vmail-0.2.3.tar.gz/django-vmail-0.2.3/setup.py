from os.path import join, dirname
from distutils.core import setup

VERSION = '0.2.3'

README = open(join(dirname(__file__), 'README.rst')).read()
REQUIREMENTS = open(join(dirname(__file__), 'requirements.txt')).readlines()

setup(
    name='django-vmail',
    version=VERSION,
    description="Virtual mail administration django app",
    author="Lewis Gunsch",
    author_email="lewis@gunsch.ca",
    url="https://github.com/lgunsch/django-vmail/",
    license='MIT',
    long_description=README,
    packages=[
        'vmail',
        'vmail.management',
        'vmail.management.commands',
        'vmail.migrations',
        'vmail.tests',
    ],
    scripts=[],
    install_requires=REQUIREMENTS,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
