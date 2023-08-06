from setuptools import setup, find_packages
import os

version = '0.1-alpha'
long_description = "\n\n".join([
    open('README.rst').read(),
    open(os.path.join("docs", "HISTORY.rst")).read()
])

setup(
    name='edeposit.amqp.antivir',
    version=version,
    description="E-Deposit module for RabbitMQ antivirus",
    long_description=long_description,
    url='https://github.com/jstavel/edeposit.amqp.antivir/',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='GPL2+',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['edeposit', 'edeposit.amqp'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'kombu',
    ],
)
