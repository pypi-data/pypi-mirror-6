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


with open('README.rst') as file:
    long_description = file.read()

setup(
    name='webpay',
    packages=['webpay', 'webpay.api', 'webpay.model'],
    version='1.0.4',
    author='webpay',
    author_email='administrators@webpay.jp',
    url='https://github.com/webpay/webpay-python',
    description='WebPay Python bindings',
    cmdclass={'test': PyTest},
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'requests==2.0.1'
    ]
)
