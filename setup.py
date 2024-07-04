from setuptools import setup, find_packages

setup(
    name='modbus_calibration',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'pymodbus>=2.5.3',
    ],
    entry_points={
        'console_scripts': [
            'modbus_calibration=modbus_calibration:main',
        ],
    },
    author='Sullivan Buchs',
    author_email='sullivan.buchs@idonus.com',
    description='Script for calibrate UV-EXP-CU-GEN3 by Modbus TCP',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/idonus/UVEXPCUGEN3-Modbus-calibration',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

