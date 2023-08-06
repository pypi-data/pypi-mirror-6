from setuptools import setup


setup(
    name='Flask-Jsonpify',
    version='1.3',
    url='https://github.com/wcdolphin/flask-jsonpify',
    license='MIT',
    author='Cory Dolphin',
    author_email='wcdolphin@gmail.com',
    description="A simple Flask extension extending Flask's core jsonify"
    " functionality to support JSON-Padded responses, using the callback specified in the querystring",
    long_description=__doc__,
    py_modules=['flask_jsonpify'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)