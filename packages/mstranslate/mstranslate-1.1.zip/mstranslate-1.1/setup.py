from distutils.core import setup


setup(
    name='mstranslate',
    packages=['mstranslate'],  # this must be the same as the name above
    version='1.1',
    description='Microsoft(Bing) translate API for python3',
    author='kk',
    author_email='bebound@gmail.com',
    url='https://github.com/bebound/Python-Microsoft-Translate-API',  # use the URL to the github repo
    download_url='https://github.com/bebound/Python-Microsoft-Translate-API/tarball/1.0',
    keywords=['translate', 'api'],  # arbitrary keyword
    install_requires=['requests >= 2.2.1',],
    classifiers=[],
)