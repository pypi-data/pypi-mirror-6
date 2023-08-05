import setuptools

setuptools.setup(
    name="pycube2crypto",
    version="0.1",
    packages=["cube2crypto"],
    package_dir={'' : 'src'},
    install_requires=["pycrypto"],
    author="Chasm",
    author_email="fd.chasm@gmail.com",
    url="https://github.com/fdChasm/pycube2crypto",
    license="MIT",
    description="An implementation of the cube2 cryptography functions in pure python.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
)
