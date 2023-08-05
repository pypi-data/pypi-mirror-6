from setuptools import setup

setup(
    name='Flask-Staticify',
    version='0.1.0',
    url='https://github.com/mstolyarchuk/flask-staticify',
    license='BSD',
    author='Maxim Stolyarchuk',
    author_email='maxim.stolyarchuk@gmail.com',
    description='Makes Flask possible to look for static files in the custom folder as a fallback',
    py_modules=['flask_staticify'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
