import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-webnodes',
    version='0.0.3',
    description='Re-usable bussiness components, modular units on a page',
    long_description=read('README.md'),
    author='iamsk',
    author_email='iamsk.info@gmail.com',
    url='https://github.com/iamsk/django-webnodes',
    packages=find_packages(exclude=('examples',)),
    install_requires=[
        "django>=1.3.7,<1.6",
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    zip_safe=False,
)
