from setuptools import setup, find_packages

setup(
    name='tengs-cli',
    description="cli for tengs.ru",
    version='0.0.5',
    # packages=['towelstuff',],
    license='MIT',
    author="Kirill Mokevnin",
    author_email="mokevnin@gmail.com",
    url="http://tengs.ru",
    long_description=open('README.txt').read(),
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'requests'
    ],
    entry_points = {
        'console_scripts': ['tengs=tengs_cli.cli:main'],
    }
)
