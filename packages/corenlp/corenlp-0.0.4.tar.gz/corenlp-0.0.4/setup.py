from setuptools import setup

setup(
    name = 'corenlp',
    packages = ['corenlp'],
    version = '0.0.4',
    description = 'A python wrapper for the Stanford CoreNLP java library.',
    author='Chris Kedzie',
    author_email='kedzie@cs.columbia.edu',
    url='www.github.com/kedz',
    install_requires=[
        'markdown',
    ]

)
                    
