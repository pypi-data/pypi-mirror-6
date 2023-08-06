from setuptools import setup


setup(
    name='tangled.sqlalchemy',
    version='0.1a3',
    description='Tangled SQLAlchemy integration',
    long_description=open('README.rst').read(),
    url='http://tangledframework.org/',
    download_url='https://github.com/TangledWeb/tangled.sqlalchemy/tags',
    author='Wyatt Baldwin',
    author_email='self@wyattbaldwin.com',
    packages=[
        'tangled',
        'tangled.sqlalchemy',
    ],
    install_requires=[
        'tangled>=0.1a7',
        'SQLAlchemy',
    ],
    extras_require={
        'dev': [
            'tangled[dev]>=0.1a7',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
