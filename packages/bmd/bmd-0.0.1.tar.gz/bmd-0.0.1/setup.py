from setuptools import setup

setup(
    name="bmd",
    version="0.0.1",
    url="https://github.com/maralla/bmd",
    license="MIT",
    author="Maralla",
    author_email="maralla.ai@gmail.com",
    description="Baidu 320k Music Downloader",
    long_description=open("README.md").read(),
    packages=["bmd"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "bmd = bmd.bmd:main"
        ]
    }
)
