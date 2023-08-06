from setuptools import find_packages, setup

version = '0.0.1.0'

description = """
The Subbehave module exposes `Behave <http://pythonhosted.org/behave/>`_ step outcomes as commands for consumption by another process.
Additional commands are provided for transitions from feature to scenario and from scenario to step.
A consumer can provide additional commands for Behave to emit.
Behave hooks typically emit these commands to alter the state of the consumer.
A Django-testing consumer, `Djbehave <https://github.com/popham/djbehave>`_, was developed in parallel with this module, and it should serve as a model for additional consumers.
"""

setup(
    name="subbehave",
    description="Provide Behave step outcomes for consumption by another process.",
    version="%s" % version,
    author="Tim Popham",
    author_email="popham@uw.edu",
    url="https://github.com/popham/subbehave",
    download_url="https://github.com/popham/subbehave/archive/%s.tar.gz" % version,
    packages=find_packages('.', exclude=()),
    install_requires=[
        'django>=1.4.1',
        'behave>=1.2.3'],
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'],
    long_description = description,
    keywords='behave subbehave django gherkin')
