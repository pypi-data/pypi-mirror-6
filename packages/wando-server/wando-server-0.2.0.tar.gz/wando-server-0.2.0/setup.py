from setuptools import setup

setup(
    name='wando-server',
    version='0.2.0',
    url='https://github.com/fholiveira/wando-server',
    license='BSD',
    author='Fernando Oliveira',
    author_email='fernando@fholiveira.com',
    description='A beautiful web server for development',
    long_description=open('README.rst').read(),
    py_modules=['wando'],
    zip_safe=False,
    platforms='any',
    install_requires=['blessings', 'colorama', 'werkzeug'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
