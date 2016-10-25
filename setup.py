from setuptools import setup

# setup
setup(
    name='ChaosProxy',
    version='0.0.1',
    description='ChaosProxy is a proxy server that causes delays and drops in requests and responses.',
    url='http://github.com/mcmartins/chaosproxy',
    author='Manuel Martins',
    author_email='manuelmachadomartins@gmail.com',
    license='Apache 2.0',
    packages=['chaosproxy'],
    package_data={'chaosproxy': ['conf.json']},
    requires=['argparse'],
    install_requires=[
        'argparse'
    ],
    zip_safe=False
)
