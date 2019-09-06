import setuptools


setuptools.setup(
    name='mk-log-analyzer',
    packages=setuptools.find_packages(
        exclude=[
            '*.tests',
        ],
    ),
    entry_points={
        'console_scripts': [
            'log-analyzer = log_analyzer.cli:main',
        ],
    },
    install_requires=[
        'importlib-metadata',
    ],
    setup_requires=[
        'setuptools_autover',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.7',
)
