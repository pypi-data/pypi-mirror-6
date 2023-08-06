from setuptools import setup
import sites_lockdown

setup(
    name='Django-Sites-Lockdown',
    version=sites_lockdown.__version__,
    packages=['sites_lockdown'],
    license='MIT License',
    description='Remove the ability to add or edit sites in Django\'s admin panel.',
    long_description=open('README.rst').read(),
    author='Richard Ward',
    author_email='richard@richard.ward.name',
    url='https://github.com/RichardOfWard/django-sites-lockdown',
    test_suite='tests',
    install_requires=['django'],
)
