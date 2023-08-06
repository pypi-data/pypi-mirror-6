# encoding: utf-8

from setuptools import setup


def get_readme():
    return open('README.rst').read()

def get_requirements():
    return open('requirements.txt').read().split()

setup_configs = dict(

    name='xmlpumpkin',
    version='0.1',
    license='BSD',
    url='https://github.com/drowse314-dev-ymat/xmlpumpkin',
    author='ymat',
    author_email='drowse314@gmail.com',
    description='CaboCha output-XML accessor',
    long_description=get_readme(),
    keywords='cabocha nlp xml parsing',
    platforms=['any'],

    packages=['xmlpumpkin'],
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ],

)


if __name__ == '__main__':
    setup(**setup_configs)
