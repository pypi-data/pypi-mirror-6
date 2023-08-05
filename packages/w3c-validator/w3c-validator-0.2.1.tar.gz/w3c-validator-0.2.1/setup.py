try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = ['requests>=2.2.0']

setup(
    name='w3c-validator',
    version='0.2.1',
    description='W3C panel for Django Debug Toolbar using requests.',
    author='Albert O\'Connor',
    author_email='iqc@albertoconnor.ca',
    url='https://bitbucket.org/amjoconn/w3c_validator',
    packages=['w3c_validator'],
    package_dir={'w3c_validator': 'w3c_validator'},
    package_data={'': ['LICENSE', 'README.md'], 'w3c_validator': ['templates/w3c_validator/*.html']},
    install_requires=requires,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
