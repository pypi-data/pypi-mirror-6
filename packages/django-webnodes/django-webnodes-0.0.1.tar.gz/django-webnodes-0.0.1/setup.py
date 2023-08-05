from setuptools import setup, find_packages

setup(
    name='django-webnodes',
    version='0.0.1',
    description='Re-usable bussiness components, modular units on a page',
    long_description=open('README.md').read(),
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
