#!/usr/bin/env python
from setuptools import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys
        import subprocess

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='django-sofort',
    version='0.0.1',
    description='Django implementation of the Sofort.com API',
    author='codingjoe',
    url='https://github.com/codingjoe/django-sofort',
    author_email='info@johanneshoppe.com',
    license='MIT License',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    packages=['sofort'],
    include_package_data=True,
    requires=['django (>=1.3.1)', 'dict2xml (>=1.1)', 'pymoneyed (>=0.5)', 'beautifulsoup4 (>=4.0)',
              'pythondateutil (>=2.2)'],
    install_requires=['django>=1.3.1', 'dict2xml>=1.1', 'py-moneyed>=0.5', 'beautifulsoup4>=4.0',
                      'python-dateutil>=2.2', 'django-appconf>=0.6'],
    cmdclass={'test': PyTest},
)