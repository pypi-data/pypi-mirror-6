from setuptools import setup

setup(
    name='Thriftipy',
    version='0.0.1-dev',
    url='http://github.com/barunsthakur/thriftipy',
    license='MIT',
    author='Barun',
    author_email='barunsthakur@gmail.com',
    description='Tool for auto-generation and packaging thrift idls for Python',
    py_modules=['thriftipy'],
    zip_safe=False,
    platforms='Unix Like',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License'
    ],
)
