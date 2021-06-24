import setuptools 

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="dicom_to_cnn",                     # This is the name of the package
    version="0.73",                        # The initial release version
    author="",                     # Full name of the author
    description="Python Library to handle Input / Output conversion in Dicom <=> Convolutional Neural Network ",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    url = 'https://github.com/wendyrvllr/Dicom-To-CNN',   # Provide either the link to your github or to your website
    download_url = 'https://github.com/wendyrvllr/Dicom-To-CNN/archive/refs/tags/72.tar.gz',
    packages=setuptools.find_packages(),    # List of all python modules to be installed
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.7',                # Minimum version requirement of the package
    install_requires=['fpdf==1.7.2',
                    'imageio==2.9.0',
                    'opencv_python==4.5.1.48',
                    'matplotlib==3.4.2',
                    'numpy>=1.19',
                    'pandas==1.2.3',
                    'Pillow==8.2.0',
                    'plotly_express==0.4.1',
                    'pydicom_seg==0.2.3',
                    'pydicom==2.1.2',
                    'pyradiomics==3.0.1',
                    'scikit-image==0.18.1',
                    'scipy==1.6.3',
                    'SimpleITK==2.0.2']                     # Install other dependencies if any
)