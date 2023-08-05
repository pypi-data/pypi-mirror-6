from setuptools import setup, find_packages

setup(
    name='django-homebanking',
    version='0.2',
    description='Django appp to analyse and present data from homebanking system',
    author='Soren Hansen',
    author_email='soren@linux2go.dk',
    url='http://github.com/sorenh/python-django-homebanking',
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    keywords='homebanking',
    install_requires=[
        'django',
        'django-ordered-model',
        'south',
        'sparnord',
    ],
)
