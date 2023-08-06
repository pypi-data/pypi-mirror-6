# Causes `python setup.py test` to not crash.
# See https://groups.google.com/forum/#!msg/nose-users/fnJ-kAUbYHQ/_UsLN786ygcJ
import multiprocessing
from setuptools import setup

setup(name='urbandict',
        version='0.3',
        url="https://github.com/novel/py-urbandict",
        author="Roman Bogorodskiy",
        author_email="bogorodskiy@gmail.com",
        py_modules=['urbandict'],
        scripts=['urbandicli'],
        classifiers=[
                "Programming Language :: Python :: 2",
                "Programming Language :: Python :: 3",
            ],
        )
