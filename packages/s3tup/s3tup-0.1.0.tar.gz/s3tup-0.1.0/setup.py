from setuptools import setup

setup(
    name='s3tup',
    version='0.1.0',
    description='Declarative configuration management and deployment tool for amazon s3',
    keywords='s3 declarative config deploy',
    url='http://github.com/HeyImAlex/s3tup',
    author='Alex Guerra',
    author_email='alex@heyimalex.com',
    license='MIT',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2.7',
    ],
    packages=['s3tup'],
    install_requires=[
        'requests',
        'argparse',
        'pyyaml',
        'beautifulsoup4',
        'gevent>=1.0',
    ],
    entry_points = {
      'console_scripts': ['s3tup=s3tup.cli:main'],
    },
    zip_safe=False,
    test_suite = 'nose.collector',
    tests_require = ['nose>=1.0', 'mock>=1.0']
)