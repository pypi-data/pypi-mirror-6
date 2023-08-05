# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='AbakaffeNotifier',
    version='1.0.0',
    author='Stein-Otto Svorstøl',
    author_email='steinotto.svorstol@gmail.com',
    packages=['pynma'],
    scripts=['checkCoffeeMaker.py'],
    url='http://pypi.python.org/pypi/AbakaffeNotifier/',
    description='Notifies phone when Abakaffe is ready.',
    install_requires=[
        "requests >= 1.2.3",
    ],
)