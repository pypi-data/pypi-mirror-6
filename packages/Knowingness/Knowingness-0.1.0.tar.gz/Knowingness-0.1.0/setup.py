from distutils.core import setup

setup(
    name='Knowingness',
    version='0.1.0',
    author='Michael Stitt',
    author_email='michaelstitt10@hotmail.com',
    packages=['knowingness', 'knowingness.social'],
    license='LICENSE.txt',
    description='Social Network Analytics',
    long_description=open('README.txt').read(),
    install_requires="requests >= 2.3.0",
)

