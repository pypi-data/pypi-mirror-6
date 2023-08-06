from setuptools import setup, find_packages

setup(
    name='cejob',
    version='0.0.6',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    url='https://bitbucket.org/cyberegoorg/cejob',
    license='BSD',
    author='Ondra Voves',
    author_email='o.voves@gmail.com',
    description='Multiprocessing stuff',
    install_requires=[
        'setuptools>=0.6b1',
    ],
)
