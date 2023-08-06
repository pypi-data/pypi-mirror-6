import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-restviews',
    version='1.0-rc1',
    packages=['restviews'],
    include_package_data=True,
    license='MIT',  # example license
    description='REST-based Django CrUD-Views',
    long_description=README,
    url='https://github.com/dploeger/django-restviews',
    author='Dennis Ploeger',
    author_email='develop@dieploegers.de',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License', # example license
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Development Status :: 5 - Production/Stable',
    ],
    zip_safe = False,
    install_requires = [
        "Django >= 1.6",
    ]
)
