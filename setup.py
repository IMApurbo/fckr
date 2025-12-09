from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fckr",
    version="1.3",
    author="AKM Korishee Apurbo",
    author_email="bandinvisible8@gmail.com",
    description="FCKR – The Ultimate Brute Forcer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IMApurbo/fck",  
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "rich>=13.3.5",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "fckr = fckr.fckr:main",
        ],
    },
    license="MIT",  # Explicitly set the license instead of `license-file`
    include_package_data=True,  # Ensure additional files like LICENSE are included
)
