from setuptools import setup, find_packages

setup(
    name='sweeper',
    version='0.1',
    packages=find_packages(),
    url='https://bitbucket.org/dominofire/sweeper',
    license='',
    author='Fernando Aguilar',
    author_email='fer.aguilar.reyes@gmail.com',
    description='Workflow execution on cloud environments',
    # Remember to keep requirements.txt updated
    install_requires=[
        'pandas >= 0.14.1',
        'azure < 1.0',
        'scp >= 0.8.0',
        'paramiko >= 1.15.2',
        'PyYAML >= 3.11',
        'selenium',
        'click',
    ],
    entry_points='''
    [console_scripts]
    sweeper=sweeper.cli.puppet:cli
    '''
)
