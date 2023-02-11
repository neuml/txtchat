# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    DESCRIPTION = f.read()

setup(
    name="txtchat",
    version="0.0.1",
    author="NeuML",
    description="Conversational search and workflows for all",
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/neuml/txtchat",
    project_urls={
        "Documentation": "https://github.com/neuml/txtchat",
        "Issue Tracker": "https://github.com/neuml/txtchat/issues",
        "Source Code": "https://github.com/neuml/txtchat",
    },
    license="Apache 2.0: http://www.apache.org/licenses/LICENSE-2.0",
    packages=find_packages(where="src/python"),
    package_dir={"": "src/python"},
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
)
