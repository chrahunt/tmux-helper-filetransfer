from setuptools import setup, find_packages
from pathlib import Path


long_description_src = Path(__file__).parent / 'README.md'


setup(
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Terminals',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'Topic :: Utilities',
    ],
    description='file transfer cli utility for tmux',
    entry_points={
        'console_scripts': [
            'tmux-helper-filetransfer=tmux_helper_filetransfer.cli:main'
        ]
    },
    license='MIT',
    long_description=long_description_src.read_text(encoding='utf-8'),
    long_description_content_type='text/markdown',
    name='tmux-helper-filetransfer',
    packages=find_packages(),
    python_requires='~=3.6',
    setup_requires=[
        'setuptools >=38.6',
        'wheel >= 0.31.0',
        'twine >= 1.11.0',
    ],
    url='https://github.com/chrahunt/tmux-helper-filetransfer',
    version='0.1.0',
)
