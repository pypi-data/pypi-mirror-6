import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djarcheology-agency',
    version='0.1',
    packages=['agency'],
    include_package_data=True,
    license='GNU General Public License v3',
    description='A Django app to manage people and their organizational affiliations from the perspective of \
                archeological research.',
    long_description=README,
    url='http://www.mankatostatearcheology.org/',
    author='Andrew Brown',
    author_email='andrew@mankatostatearcheology.org',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)