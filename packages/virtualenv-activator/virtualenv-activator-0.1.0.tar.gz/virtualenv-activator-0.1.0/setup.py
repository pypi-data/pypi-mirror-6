from setuptools import setup


with open('README.rst') as fp:
    long_description = fp.read()

setup(
    name='virtualenv-activator',
    version='0.1.0',
    description='A better activate script for Python\'s virtualenv',
    long_description=long_description,
    url='http://github.com/jnrbsn/virtualenv-activator',
    author='Jonathan Robson',
    author_email='jnrbsn@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='virtualenv',
    install_requires=['virtualenv'],
    data_files=[('etc', ['activate.sh'])],
)
