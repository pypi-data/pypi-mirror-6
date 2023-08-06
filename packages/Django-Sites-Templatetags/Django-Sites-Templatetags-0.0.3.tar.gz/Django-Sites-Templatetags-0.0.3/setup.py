from setuptools import setup
import sites_templatetags

setup(
    name='Django-Sites-Templatetags',
    version=sites_templatetags.__version__,
    packages=['sites_templatetags', 'sites_templatetags.templatetags'],
    license='MIT',
    description='The missing templatetags to get the current site from django.contrib.sites.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard@richard.ward.name',
    url='https://github.com/RichardOfWard/django-sites-templatetags',
)
