import setuptools


def get_description():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


def get_next_version():
    version = {
        "major": None,
        "minor": None,
        "patch": None
    }

    with open("version", "r") as f:
        lines = f.readlines()
        version["major"] = lines[0]
        version["minor"] = lines[1]
        version["patch"] = str(int(lines[2]) + 1)

    with open("version", "w") as f:
        f.writelines([version["major"], version["minor"], version["patch"], ''])

    return version


version = get_next_version()
readme = get_description()

setuptools.setup(
    name="flockai",
    version='.'.join([version["major"][:-1], version["minor"][:-1], version["patch"]]),
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