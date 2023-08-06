# coding=utf-8
import django_sae
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()
with open('HISTORY.md') as f:
    history = f.read()

setup(
    name='django-sae',
    version=django_sae.__version__,
    description='for django in sae',
    long_description=readme + '\n\n' + history,
    author='smallcode',
    author_email='45945756@qq.com',
    url='https://github.com/smallcode/django-sae',
    packages=find_packages('django_sae'),
    package_dir={'': 'django_sae'},
    include_package_data=True,
    install_requires=[
        'django>=1.6.2,<1.7',
    ],
    license=django_sae.__license__,
    zip_safe=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

