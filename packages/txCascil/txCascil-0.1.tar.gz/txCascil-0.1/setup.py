import setuptools

packages = [
    'txCascil',
    'txCascil.client',
    'txCascil.client.authentication_controllers',
    'txCascil.packings',
    'txCascil.permissions',
    'txCascil.server',
    'txCascil.server.authentication_controllers',
    'txCascil.transports',
    'txCascil.utils',
]

setuptools.setup(
    name="txCascil",
    version="0.1",
    packages=packages,
    package_dir={'' : 'src'},
    install_requires=["twisted", 'pycube2crypto', "simplejson", "simple_json", "pyclj"],
    author="Chasm",
    author_email="fd.chasm@gmail.com",
    url="https://github.com/fdChasm/txCascil",
    license="MIT",
    description="(Twisted) Cube Ancillary Service Communication Interface Layer",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
)
