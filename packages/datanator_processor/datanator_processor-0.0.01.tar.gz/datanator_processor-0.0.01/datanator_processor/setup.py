from distutils.core import setup

import codecs 
try: 
    codecs.lookup('mbcs') 
except LookupError: 
    ascii = codecs.lookup('ascii') 
    func = lambda name, enc=ascii: {True: enc}.get(name=='mbcs') 
    codecs.register(func) 

setup(
    name='datanator_processor',
    version='0.0.0',
    description=open('README.txt').read(),
    url='http://bitbucket.org/ctmoses/datanator_processing',
    author='David Y. Stephenson',
    author_email='david@davidystephenson.com',
    packages=['datanator_processor'],
    license='Proprietary',
    long_description=open('README.txt').read(),
    install_requires=['requests'],
)
