from setuptools import find_packages, setup

from header_auth import __version__


setup(
    name='django-header-auth',
    version=__version__,
    description='Django middleware for authorizing requests based on headers.',
    author='LocalMed',
    author_email='pete.browne@localmed.com',
    url='https://bitbucket.org/localmed/django-header-auth',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
