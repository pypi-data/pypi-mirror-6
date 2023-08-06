import os
from setuptools import setup

def readMD(fname):
    # Utility function to read the README file.
    full_fname = os.path.join(os.path.dirname(__file__), fname)
    if 'PANDOC_PATH' in os.environ:
        import pandoc
        pandoc.core.PANDOC_PATH = os.environ['PANDOC_PATH']
        doc = pandoc.Document()
        with open(full_fname) as fhandle:
            doc.markdown = fhandle.read()
        return doc.rst
    else:
        with open(full_fname) as fhandle:
            return fhandle.read()

setup(
    name='allset',
    version="1.0.0",
    description='Generates dynamic bindings for module imports',
    long_description=readMD('README.md'),
    packages=['allset'],
    author='Matthew Seal',
    author_email='mseal@opengov.com',
    url='https://github.com/OpenGov/allset',
    license='New BSD',
    download_url='https://github.com/OpenGov/allset/tarball/v1.0.0',
    keywords=['importing'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2 :: Only'
    ]
)
