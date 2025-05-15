# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    # Remove GitHub dark mode images
    DESCRIPTION = "".join([line for line in f if "gh-dark-mode-only" not in line])

setup(
    name="txtchat",
    version="0.3.0",
    author="NeuML",
    description="Build autonomous agents, retrieval augmented generation (RAG) processes and language model powered chat applications ",
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
    keywords="search embedding machine-learning nlp",
    python_requires=">=3.10",
    install_requires=["huggingface-hub>=0.19.0", "pyyaml>=5.3", "rocketchat_async>=4.2.0", "txtai>=8.5.0"],
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
