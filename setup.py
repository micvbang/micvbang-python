import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="micvbang",
    version="0.0.1",
    author="Michael Bang",
    author_email="mic@vbang.dk",
    description="micvbang's often used utility functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/micvbang/micvbang-python",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
)
