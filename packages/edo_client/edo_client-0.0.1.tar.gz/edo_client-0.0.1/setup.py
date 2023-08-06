from setuptools import setup, find_packages

kw = dict(
    name = 'edo_client',
    version = '0.0.1',
    description = 'Everydo OAuth 2 API Python SDK',
    long_description = "Everydo OAuth 2 API Python SDK",
    author = 'panjy',
    author_email = 'whchen1080@gmail.com',
    url = 'https://github.com/everydo/python-sdk',
    download_url = 'https://github.com/everydo/python-sdk',
    packages = find_packages(),
    install_requires = ['py-oauth2>=0.0.5'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])

setup(**kw)
