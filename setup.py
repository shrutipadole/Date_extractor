import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="date_extractor",
    version="0.0.1",
    author="Shruti Padole",
    author_email="shrutipadole339@gmail.com",
    description="exhaustive date detector",
    long_description=long_description,
    long_description_content_type="text",
    url="https://github.com/shrutipadole/date_extractor/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
