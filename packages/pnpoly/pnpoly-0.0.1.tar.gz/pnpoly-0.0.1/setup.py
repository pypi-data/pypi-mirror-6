from distutils.core import setup, Extension

setup(
    name="pnpoly",
    version="0.0.1",
    ext_modules=[Extension(
        "pnpoly", ["pnpoly.c"]
    )]
)
