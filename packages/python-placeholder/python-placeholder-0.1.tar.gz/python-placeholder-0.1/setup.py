from setuptools import setup, find_packages
from pip.req import parse_requirements
install_reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name='python-placeholder',
    version='0.1',
    description='Placeholder is a simple little python module that creates (drumroll..) placeholder images, based on work of Martin Marcher',
    author="Visgean Skeloru",
    url='https://github.com/Visgean/python-placeholder',
    packages=['placeholder'],
    include_package_data=True,
    install_requires=reqs,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='placeholder,images',
    )
