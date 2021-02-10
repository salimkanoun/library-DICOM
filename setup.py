import setuptools 

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="Dicom-To-CNN",                     # This is the name of the package
    version="0.0.1",                        # The initial release version
    author="",                     # Full name of the author
    description="Python Library to handle Input / Output conversion in Dicom <=> Convolutional Neural Network ",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    url = 'https://github.com/wendyrvllr/Dicom-To-CNN',   # Provide either the link to your github or to your website
   download_url = 'https://github.com/wendyrvllr/Dicom-To-CNN/archive/v1.0.tar.gz',
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3.7, 3.8",
        "License :: GPL-3.0 License ",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.6',                # Minimum version requirement of the package
    py_modules=["dicom-to-cnn"],             # Name of the python package
    package_dir={'':'Dicom-To-CNN/library_dicom'},     # Directory of the source code of the package
    install_requires=[]                     # Install other dependencies if any
)