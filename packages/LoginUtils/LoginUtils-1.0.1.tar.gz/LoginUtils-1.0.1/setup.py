from setuptools import setup, find_packages

config = {
        'name' : 'LoginUtils',
        'version' : '1.0.1',
        'author' : 'Kyle Roux',
        'author_email' : 'kyle@level2designs.com',
        'packages' : find_packages(),
        'package_dir' : {'':'.'},
}
setup(**config)
