from setuptools import setup

setup(
    name='wando-server',
    version='0.1.0',
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
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
