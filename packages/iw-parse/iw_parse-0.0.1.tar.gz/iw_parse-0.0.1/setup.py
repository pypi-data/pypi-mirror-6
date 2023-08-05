from distutils.core import setup

with open("iw_parse/README.md") as f:
    long_description = f.read()

setup(name="iw_parse",
        packages=["iw_parse"],
        version="0.0.1",
        author="Cuzzo Yahn",
        author_email="yahn007@outlook.com",
        description="An iwlist parser.",
        license="BSD",
        keywords="iwlist parser",
        url="http://github.com/cuzzo/iw_parse",
        long_description=long_description,
        scripts=["iw_parse/iw_parse"])
