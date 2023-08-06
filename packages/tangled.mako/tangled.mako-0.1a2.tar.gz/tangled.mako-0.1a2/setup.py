from setuptools import setup


setup(
    name='tangled.mako',
    version='0.1a2',
    description='Tangled Mako integration',
    long_description=open('README.rst').read(),
    url='http://tangledframework.org/',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    include_package_data=True,
    packages=[
        'tangled',
        'tangled.mako',
        'tangled.mako.tests',
    ],
    install_requires=[
        'tangled.web>=0.1a5',
        'Mako>=0.9.1',
    ],
    extras_require={
        'dev': [
            'tangled.web[dev]>=0.1a5',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
