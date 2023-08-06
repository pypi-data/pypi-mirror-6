import os
from setuptools import setup


CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]


setup(
    name='django-socialshareprivacy',
    version='1.5.1',
    author='Adi Sieker',
    author_email='adi@sieker.io',
    packages=['socialshareprivacy',],
    include_package_data=True,
    package_data={'socialshareprivacy': ['templatetags/*',]},
    url='http://github.com/adsworth/django-socialshareprivacy/',
    platforms=['OS Independent'],
    license='LICENSE',
    classifiers=CLASSIFIERS,
    description='A Django application for the heise.de socialshareprivacy jQuery plugin.',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    install_requires=[
        "Django >= 1.5",
    ],
)
