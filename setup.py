import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flockai",
    version="0.0.6",
    author="kosnet",
    author_email="kosnet@kosnet.com",
    description="A machine learning webots extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/unic-ailab/flockai-working",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)