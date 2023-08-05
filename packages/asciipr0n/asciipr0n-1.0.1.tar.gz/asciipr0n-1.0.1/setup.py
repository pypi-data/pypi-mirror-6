import setuptools

setuptools.setup(
    name='asciipr0n',
    version='1.0.1',
    description='Display NSFW images in your logfiles',
    author='Rob Britton',
    author_email='rob@robbritton.com',
    keywords=[],
    packages=['asciipr0n'],
    package_dir={"asciipr0n": "asciipr0n"},
    package_data={"asciipr0n": ["data/*.txt"]},
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Logging"
    ],
    long_description="""\
    Silly function for displaying NSFW in your logfiles.
""",
)
