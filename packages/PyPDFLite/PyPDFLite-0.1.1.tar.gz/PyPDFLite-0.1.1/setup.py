from distutils.core import setup

setup(
    name='PyPDFLite',
    version='0.1.1',
    author='Katerina Hanson',
    author_email='katerina.hanson@gmail.com',
    packages=['pypdflite', 'pypdflite.pdfobjects'],
    scripts=['bin/runexamples.py'],
    url='http://pypi.python.org/pypi/PyPDFLite/',
    license='LICENSE.txt',
    description='Simple PDF Writer.',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
