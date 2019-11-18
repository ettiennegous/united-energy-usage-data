import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unitedenergy-usage-data",
    version="0.0.1",
    author="Ettienne Gous",
    author_email="ettiennegous@hotmail.com",
    description="Energy Easy helper class",
    long_description="This helper class is to read electricity usage data from Unit Energy's Energy Easy portal.  United Energy is an electricity distributor for Melbourne Victoria's south eastern suburbs and the Mornington Peninsula.",
    long_description_content_type="text/markdown",
    url="https://github.com/ettiennegous/united-energy-usage-data",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)