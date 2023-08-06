from distutils.core import setup

# TODO Synchronize version with __init__.py of pytheas package.

setup(
    name = "Pytheas",
    version = "0.1.0",
    packages = ["pytheas",],
    license = "MIT",
    long_description = open("readme.markdown").read(),
)
