import setuptools
from pathlib import Path

projectroot = Path(__file__).parent.resolve()

# To incorporate README as long desription:
# Uncomment below and relevant line in setuptools.setup
with open("README.md", "r") as f:
    long_description = f.read()

# To include version number:
#
# Single source version number using nbread/VERSION.txt
# Ensure that there is a MANIFEST.in file to include VERSION.txt in packaging
# Comment below:
version = "0.1.0"
# Uncomment below, and relevant line in setuptools.setup
# with open(projectroot / "nbread/VERSION.txt", "r") as f:
#     version = f.read().strip()

setuptools.setup(
    # Important args
    name="nbread",
    version=version,
    author="Tan, Nian Wei",
    description="Read Jupyter notebooks from the command line",
    packages=["nbread"],
    install_requires=[
        "rich",
        "pygments",
    ],  # SPECIFY DEPENDENCIES HERE e.g. ["pandas", "numpy"]
    # Less important args
    # author_email="YOUR-EMAIL-HERE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tnwei/nbread",
    # python_requires=">=3.6", # SPECIFY REQUIRED PYTHON VERSION
    # include_package_data=True # Uncomment if using MANIFEST.in
    entry_points={
        "console_scripts": [
            "nbread = nbread:run",
        ],
    },
)
