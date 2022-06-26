import setuptools


def get_description():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description

readme = get_description()

setuptools.setup(
    name="flockai",
    version='0.0.1',
    author="kosnet",
    author_email="kosnet@kosnet.com",
    description="A machine learning webots extension",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/unic-ailab/flockai-working",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)