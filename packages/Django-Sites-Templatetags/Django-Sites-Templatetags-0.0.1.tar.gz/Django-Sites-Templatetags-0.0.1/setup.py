from setuptools import setup
import sites_templatetags

setup(
    name='Django-Sites-Templatetags',
    version=sites_templatetags.__version__,
    packages=['sites_templatetags', 'sites_templatetags.templatetags'],
    license='MIT',
    description='Remove the ability to add or edit sites in Django\'s admin panel.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard@richard.ward.name',
    url='https://github.com/RichardOfWard/django-sites-templatetags',
)
