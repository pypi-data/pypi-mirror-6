from setuptools import setup, find_packages


setup(
    author="Jonas Obrist",
    author_email="ojiidotch@gmail.com",
    name='modman',
    version='1',
    description='Tool for managing game mods',
    url='https://github.com/ojii/modman',
    license='BSD License',
    platforms=['OS Independent'],
    install_requires=[
        'requests',
        'patool',
        'docopt'
    ],
    packages=find_packages(),
    zip_safe=False,
    test_suite='tests',
    entry_points = {
        'console_scripts': [
            'modman = modman.api:cli',
        ]
    }
)
