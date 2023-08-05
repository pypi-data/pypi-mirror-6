"""
setup.py file for building fool components.

Nothing in this file should need to be edited, please see accompanying
package.json file if you need to adjust metadata about this package.

Borrowed almost wholesale from Armstrong http://armstrongcms.org/
"""

from setuptools import setup, find_packages
import json

info = json.load(open("package.json"))

version = '0.1'
def convert_to_str(d):
    """
    Recursively convert all values in a dictionary to strings

    This is required because setup() does not like unicode in
    the values it is supplied.
    """
    d2 = {}
    for k, v in d.items():
        k = str(k)
        if type(v) in [list, tuple]:
            d2[k] = [str(a) for a in v]
        elif type(v) is dict:
            d2[k] = convert_to_str(v)
        else:
            d2[k] = str(v)
    return d2

info = convert_to_str(info)

setup_kwargs = {
    "author": "Brian Faherty",
    "author_email": "anothergenericuser@gmail.com",
    "url": "https://github.com/themotleyfool/django-class-backed-field",
    "packages": find_packages(),
    "include_package_data": True,
    "version": version,
    "classifiers": [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    "setup_requires": [
        'setuptools-git==1.0'
    ]
}

setup_kwargs.update(info)
setup(**setup_kwargs)
