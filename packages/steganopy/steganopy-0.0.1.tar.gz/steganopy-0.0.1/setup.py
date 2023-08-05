from setuptools import setup, find_packages


setup(
    name="steganopy",
    version='0.0.1',
    description="A steganography tool written in Python",
    long_description=file('README.rst').read(),
    author="Jarrod C. Taylor",
    author_email="jarrod.c.taylor@gmail.com",
    url="http://github.com/JarrodCTaylor/steganopy",
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries'
    ],
    tests_require=[
        'Pillow',
        'nose',
        'flake8'
    ],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'steganopy = steganopy.gui:main'
        ]
    },
    install_requires=['Pillow']
)
