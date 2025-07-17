from setuptools import setup, find_packages

setup(
    name="code-rag",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sentence-transformers>=2.2.0",
        "chromadb>=0.4.0",
        "openai>=1.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        'console_scripts': [
            'code-rag=src.cli:cli',
        ],
    },
)