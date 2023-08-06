import os

from setuptools import setup, find_packages


# https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='django-sneak-peek',
    version='0.0.1',
    description='Django template tag to hide pre-release features in a ' \
        'template',
    long_description=(
        read('README.md') + '\n\n' +
        read('CHANGELOG')),
    url='https://github.com/teddywing/django-sneak-peek',
    license='MIT',
    author='Teddy Wing',
    author_email='pypi@teddywing.com',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Django >= 1.4',
        'South'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2'
    ],
)