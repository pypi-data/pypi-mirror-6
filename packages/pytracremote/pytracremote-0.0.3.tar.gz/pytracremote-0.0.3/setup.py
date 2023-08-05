from setuptools import setup, find_packages

setup(
    name='pytracremote',
    version='0.0.3',
    description="Manager for multiple remote trac instances",
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='trac, ssh',
    author='42coffeecups.com',
    author_email='contact@42cc.co',
    url='https://github.com/42cc/pytracremote',
    packages=find_packages(),
    package_data={
        '': ['pytracremote/scripts/*'],
    },
    include_package_data=True,
    zip_safe=False,
)
