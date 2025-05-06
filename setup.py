"""
Setup file for the PAB SDK.
"""

from setuptools import setup, find_packages

setup(
    name="pab-sdk",
    version="0.1.0",
    description="Python SDK for the Project Agent Builder API",
    author="SAP",
    author_email="info@sap.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 