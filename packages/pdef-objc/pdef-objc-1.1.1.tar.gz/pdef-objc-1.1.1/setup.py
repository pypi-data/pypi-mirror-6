# encoding: utf-8
import os.path
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup


setup(
    name='pdef-objc',
    version='1.1.1',
    license='Apache License 2.0',
    description='Pdef Objective-C generator',
    long_description=open('README.md', 'r').read(),
    url='http://github.com/pdef/pdef-objc',

    author='Ivan Korobkov',
    author_email='ivan.korobkov@gmail.com',

    packages=['pdef_objc'],
    package_data={
        '': ['*.jinja2']
    },

    install_requires=[
        'pdef-compiler>=1.1'
    ],
    entry_points={
        'pdefc.generators': [
            'objc = pdef_objc:ObjectiveCGenerator',
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers'
    ]
)
