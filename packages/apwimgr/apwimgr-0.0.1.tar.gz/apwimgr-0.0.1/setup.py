from distutils.core import setup

with open("README.md") as f:
    long_description = f.read()

setup(name="apwimgr",
        packages=["apwimgr"],
        version="0.0.1",
        author="Cuzzo Yahn",
        author_email="yahn007@outlook.com",
        description="An access point-based wireless network manager.",
        license="BSD",
        keywords="wireless access point network manager",
        url="http://github.com/cuzzo/apwimgr",
        long_description=long_description)
