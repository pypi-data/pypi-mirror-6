from setuptools import setup


setup(
    name='Cryptsy',
    version='0.2.1',
    license='GNU GPL2',
    url='https://github.com/jaapz/CryptsyPythonAPI',
    author='Jaap Broekhuizen <jaapz.b@gmail.com>, '
           'Matt Joseph Smith <matt.joseph.smith@gmail.com>',
    description='A python wrapper for the Cryptsy API.',
    py_modules=['Cryptsy'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
