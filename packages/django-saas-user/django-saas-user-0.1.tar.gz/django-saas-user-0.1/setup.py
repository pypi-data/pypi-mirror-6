from setuptools import setup, find_packages

setup(
    name='django-saas-user',
    version='0.1',
    description='Multi-client Authentication/Authorization for Django',
    author='Curtis Maloney',
    author_email='curtis@commoncode.com.au',
    url='http://github.com/commoncode/gambit',
    keywords=['django',],
    packages = find_packages(exclude=['test.*']),
    zip_safe=False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    requires = [
        'Django (>=1.6)',
    ],
)
