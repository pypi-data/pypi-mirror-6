from setuptools import setup, find_packages

description="""
PostgreSQL native array fields extension for Django.
"""

setup(
    name = "djorm-ext-pgarray",
    version = '0.9',
    url = 'https://github.com/niwibe/djorm-ext-pgarray',
    license = 'BSD',
    platforms = ['OS Independent'],
    description = description.strip(),
    author = 'Andrey Antukh',
    author_email = 'niwi@niwi.be',
    maintainer = 'Andrey Antukh',
    maintainer_email = 'niwi@niwi.be',
    packages = find_packages(),
    include_package_data = False,
    install_requires = [],
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        'Topic :: Internet :: WWW/HTTP',
    ]
)
