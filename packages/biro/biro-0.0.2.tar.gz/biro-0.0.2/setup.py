from setuptools import setup

setup(
    name='biro',
    version='0.0.2',
    url='https://github.com/zweifisch/biro',
    license='MIT',
    description='bidirectional URI routing',
    keywords='bidirectional routing',
    long_description=open('README.md').read(),
    author='Feng Zhou',
    author_email='zf.pascal@gmail.com',
    packages=['biro'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: WSGI'
    ],
)
