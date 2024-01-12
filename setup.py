# pylint: disable = C0111
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    # Remove GitHub dark mode images
    DESCRIPTION = "".join([line for line in f if "gh-dark-mode-only" not in line])

setup(
    name="txtchat",
    version="0.2.0",
    author="NeuML",
    description="Retrieval augmented generation (RAG) and language model powered search applications",
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
    python_requires=">=3.8",
    install_requires=[
        "datasets>=2.8.0",
        "nltk>=3.5",
        "pandas>=1.3.5",
        "pyyaml>=5.3",
        "rocketchat_async>=1.0.1",
        "tqdm>=4.48.0",
        "txtai>=5.4.0",
    ],
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
