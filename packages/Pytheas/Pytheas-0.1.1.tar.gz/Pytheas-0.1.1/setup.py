from distutils.core import setup

# TODO Synchronize version with __init__.py of pytheas package.

setup(
    name = "Pytheas",
    version = "0.1.1",
    author = "Chad Estioco",
    author_email = "chadestioco@gmail.com",
    url = "https://github.com/skytreader/pytheas",
    packages = ["pytheas",],
    license = "MIT",
    description = "Framework for a fetch-and-send daemon.",
)
