"""
recoder
--------

Tool for coding fix.

Description:
  - When downloaded, html pages are often incorrectly decoded. For example, CP1251 page can be interpreted as ISO8859 page.

Features:
  - Supports only Cyrillic at the moment.

"""
from setuptools import setup, find_packages

setup(
    name='recoder',
    version='0.3.1',
    author='David Kuryakin',
    author_email='dkuryakin@gmail.com',
    url='https://bitbucket.org/dkuryakin/recoder',
    download_url = 'https://bitbucket.org/dkuryakin/recoder/get/master.tar.gz',
    license='mit',
    description='Tool (and lib) for coding fix.',
    keywords=['cyrillic', 'encoding', 'coding', 'fix', 'decoder', 'recoder', 'i18n'],
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    test_suite = "recoder.tests",
    packages=['recoder', 'recoder.cyrillic', 'recoder.builder'],
    include_package_data=True,
    package_data={'recoder': ['*.json']},
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)