import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="computational-factorio-hypermania", # Replace with your own username
    version="0.0.1",
    author="hypermania",
    author_email="hypermania@uchicago.edu",
    description="Computational methods for modded Factorio design.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hypermania/computational-factorio",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
