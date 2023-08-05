try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='python-poco',
    version='0.1.0',
    description='Tool to integrate your Python app with Poco.',
    long_description=readme,
    author='Johan Meiring',
    author_email='johanmeiring@gmail.com',
    url='https://github.com/johanmeiring/python-poco',
    license='LICENSE',
    packages=['poco', 'poco.test'],
    install_requires=[
        "requests >= 2.1.0",
    ],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
)
