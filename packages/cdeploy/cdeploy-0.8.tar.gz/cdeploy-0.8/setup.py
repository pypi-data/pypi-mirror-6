from setuptools import setup, find_packages

setup(
    name='cdeploy',
    version='0.8',
    description='A tool for managing Cassandra schema migrations',
    author='David McHoull',
    author_email='dmchoull@gmail.com',
    url='https://github.com/dmchoull/cdeploy',
    download_url='https://github.com/dmchoull/cdeploy/archive/v0.8.tar.gz',
    keywords=['cassandra', 'migrations'],
    packages=find_packages(),
    test_suite="cdeploy.test",
    entry_points={
        'console_scripts': [
            'cdeploy = cdeploy.migrator:main'
        ]
    }
)