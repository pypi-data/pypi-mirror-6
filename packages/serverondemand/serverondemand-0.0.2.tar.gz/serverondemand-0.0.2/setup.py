from setuptools import setup, find_packages

setup(name='serverondemand',
    version='0.0.2',
    author='Andrew Regner',
    author_email='andrew@aregner.com',
    url='https://github.com/adregner/server-on-demand',
    description='Wrapper library / script to run things on a as-needed server.',
    packages=['serverondemand'],
    scripts=[
        "bin/demand_server",
        ],
    package_data={
        'serverondemand': ['resources/*.sh', 'resources/*.py']
        },
    install_requires=[
        'pyrax',
        'paramiko'
        ])

# vim:et:fdm=marker:sts=4:sw=4:ts=4
