import distutils.core

version = "0.0.2"

distutils.core.setup(
    name="pywatch_client",
    version=version,
    py_modules=["pywatch_client", "tools"],
    author="Tom",
    author_email="wmttom@gmail.com",
    url="https://github.com/wmttom/pywatch",
    description="A simple monitor.",
    )