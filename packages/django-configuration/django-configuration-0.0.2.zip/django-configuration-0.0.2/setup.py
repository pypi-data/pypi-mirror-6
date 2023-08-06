from setuptools import setup, find_packages
import configuration

setup(
    name='django-configuration',
    version=configuration.__version__,
    packages=["configuration", "configuration.templatetags"],
    license='MIT',
    description='Configuration admin/models for Django.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard.ward@fah-designs.co.uk',
    url='https://github.com/fah-designs/django-configuration',
    install_requires=[
        'django',
        'django-polymorphic',
    ],
    test_suite='tests',
)
