from setuptools import setup

setup(
    name='signer',
    version='0.0.1',
    url='https://github.com/zweifisch/signer',
    license='MIT',
    description='a python module for message signing',
    keywords='singning',
    long_description=open('README.md').read(),
    author='Feng Zhou',
    author_email='zf.pascal@gmail.com',
    packages=['signer'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
)
