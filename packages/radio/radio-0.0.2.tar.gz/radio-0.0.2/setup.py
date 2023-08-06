from distutils.core import setup

setup(
    name='radio',
    version='0.0.2',
    author='Santiago Pestarini',
    author_email='santiago@pestarini.com.ar',
    packages=['radio', 'radio.data'],
    package_data={'radio': ['data/*.json']},
    scripts=['bin/radio'],
    url='http://pypi.python.org/pypi/radio/',
    license='LICENSE.txt',
    description='Just listen to the radio.',
    long_description=open('README.txt').read(),
)
