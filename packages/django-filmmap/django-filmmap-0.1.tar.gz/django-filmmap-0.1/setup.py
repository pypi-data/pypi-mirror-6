from setuptools import setup, find_packages

setup(
    name='django-filmmap',
    version='0.1',
    license='BSD',
    author='Risto Stevcev',
    author_email='risto1@gmail.com',
    url='https://github.com/Risto-Stevcev/django-filmmap',
    long_description=open('README.rst','r').read(),
    packages=find_packages(),
    description='An API to find movies that are playing in the San Francisco area.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Environment :: Console',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: User Interfaces',
        ], 
)
