from setuptools import setup

setup(
    name='django-d3',
    version='3.3.11',
    url='https://github.com/mikebryant/django-d3',
    description='Django package for d3',
    author='Michael Bostock',
    maintainer='Mike Bryant',
    maintainer_email='mike@mikebryant.me.uk',
    license='BSD license',
    keywords=['django', 'd3', 'staticfiles'],
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=['d3'],
    package_data={'d3': ['static/js/*.js']},
)
