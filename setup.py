from setuptools import setup
from chaosproxy.chaosproxy import __version__

setup(
    name='ChaosProxy',
    version=__version__,
    description='ChaosProxy is an http 1.0 proxy / forward server that creates unstable connections.',
    url='http://github.com/mcmartins/chaosproxy',
    author='Manuel Martins',
    author_email='manuelmachadomartins@gmail.com',
    license='MIT',
    packages=['chaosproxy'],
    package_data={'chaosproxy': ['sample-conf.json']},
    requires=['argparse'],
    install_requires=[
        'argparse'
    ],
    zip_safe=False
)
