from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = "0.1.3"

long_desc = """
Python RexPro interface
"""

setup(
    name='rexpro',
    version=version,
    description='Python RexPro interface',
    dependency_links=['https://github.com/platinummonkey/rexpro-python/archive/{0}.tar.gz#egg=rexpro-python-{0}'.format(version)],
    long_description=long_desc,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='rexster,tinkerpop,rexpro,graphdb',
    install_requires=['msgpack-python', 'six==1.6.1'],
    extra_requires={
        'develop': ['nose==1.3.0', 'coverage==3.7.1', 'tox==1.7.1'],
    },
    scripts=['run_coverage.sh'],
    author='Blake Eggleston',
    author_email='bdeggleston@gmail.com',
    maintainer='Cody Lee',
    maintainer_email='codylee@wellaware.us',
    url='https://github.com/bdeggleston/rexpro-python',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)

