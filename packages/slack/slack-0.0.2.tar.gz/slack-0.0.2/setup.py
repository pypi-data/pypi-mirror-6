from setuptools import setup

setup(
    name='slack',
    version='0.0.2',
    url='https://github.com/zweifisch/slack',
    license='MIT',
    description='a DI container',
    keywords='DI Container',
    long_description=open('README.md').read(),
    author='Feng Zhou',
    author_email='zf.pascal@gmail.com',
    packages=['slack'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
)
