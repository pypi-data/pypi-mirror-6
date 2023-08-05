from setuptools import setup, find_packages

dependencies = [
    'argcomplete>=0.6.3',
    'argh>=0.23.3',
    'pyyaml>=3.10',
    'requests>=2.1.0',
    'beautifulsoup4>=4.3.2'
    ]

setup(
    name='wutang',
    description='generate names. laugh about it.',
    keywords='wutang',
    version='1.0',
    entry_points = {'console_scripts': ['wutang=wutang.wutang:main']},
    packages = find_packages(exclude=['tests']),
    package_data = {'wutang': ['wutang.yaml']},
    author='samstav',
    author_email='smlstvnh@gmail.com',
    install_requires=dependencies,
    license='GNU GPL',
    classifiers=["Programming Language :: Python"],
    url='https://github.com/smlstvnh/wutang'
)
