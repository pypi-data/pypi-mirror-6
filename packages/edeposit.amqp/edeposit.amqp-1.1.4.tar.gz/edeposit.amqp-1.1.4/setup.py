from setuptools import setup, find_packages


version = '1.1.4'
long_description = "\n\n".join([
    open('README.rst').read(),
    open('CONTRIBUTORS.txt').read(),
    open('CHANGES.txt').read()
])

setup(
    name='edeposit.amqp',
    version=version,
    description="E-Deposit's AMQP definitions and common classes/patterns.",
    long_description=long_description,
    url='https://github.com/jstavel/edeposit.amqp/',

    author='Edeposit team',
    author_email='edeposit@email.cz',

    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='GPL2+',

    packages=find_packages(exclude=['ez_setup']),

    namespace_packages=['edeposit'],
    include_package_data=True,
    zip_safe=False,
    test_suite='edeposit.amqp.tests',
    install_requires=[
        'setuptools',
        "python-daemon>=1.5.5",
        "pika>=0.9.13",
    ]
)
