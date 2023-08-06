from setuptools import setup, find_packages


setup(
    name='python-placeholder',
    version='0.1.3',
    description='Placeholder is a simple little python module that creates (drumroll..) placeholder images, based on work of Martin Marcher',
    author="Visgean Skeloru",
    url='https://github.com/Visgean/python-placeholder',
    packages=['placeholder'],
    include_package_data=True,
    install_requires=[
        'pillow',
    ],

    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='placeholder,images',
    )
