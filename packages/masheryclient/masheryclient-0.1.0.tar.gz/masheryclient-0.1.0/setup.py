from setuptools import setup, find_packages


with open('README.rst') as fp:
    long_description = fp.read()


setup(
    name='masheryclient',
    version='0.1.0',

    description='A simple Python client library for the Mashery API',
    long_description=long_description,

    author='Devin Sevilla',
    author_email='dasevilla@gmail.com',

    url='https://github.com/dasevilla/mashery-python',
    download_url='https://github.com/dasevilla/mashery-python/tarball/master',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=[
        'requests>=1.2.0',
        'requests-auth-mashery',
    ],

    packages=find_packages(),
)
