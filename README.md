[comment]: <> (<img src="https://github.com/uafgeotools/vmod/assets/16811978/297cecd1-78d6-4146-9f7a-fc1c623f1cbf" width="300">)
<img src="https://github.com/uafgeotools/vmod/assets/16811978/aaa335b6-5e03-41b3-ae65-b7c4edf113f5" width="500">

# Versatile Modeling Of Deformation

### Authors: Mario Angarita, Ronni Grapenthin, Scott Henderson, Michael Christoffersen and Kyle Anderson

## What is VMOD?

VMOD is a python-based object oriented framework. Its main purpose is to model multiple types of geodetic data including:

- GNSS
- InSAR
- Level
- EDM
- Tilt

These observations can be interpreted with one or more analytical models that represent pressurized sources such as:

- Pressurized sphere in elastic medium
- Pressurized sphere in viscoelastic medium
- Pressurized sphere in a viscoelastic shell in elastic medium
- Pressurized prolate spheroid in elastic medium
- Dislocation (Fault/Sill) in elastic medium
- Penny shaped crack in elastic medium
- Point source in elastic medium
- Wellsite in porelastic medium
- Ring fault in elastic medium
- Regularized fault/sill in elastic medium
- Open conduit in elastic medium

The framework offers two different inversion techniques to solve for the source parameters:

- Non-linear least squares
- Bayesian approach

The inversions can include one or multiple data types in the inversion and the model can be composed by multiple sources. The user can customize or inherit current models to create complexer geometries.

![class_diag_new](https://github.com/uafgeotools/vmod/assets/16811978/914866ca-d13c-4760-b556-2bd58ce757ba)

## Setup

The first step to install the framework is to clone this repository:

```console
$git clone https://github.com/uafgeotools/vmod.git
```

Then create the environment in conda from the vmod.yml file:

```console
$conda env create -f vmod.yml 
```

## Run an inversion:

In this repository we included several notebooks to show the steps necessary to run an inversion using [GNSS](dvd_gnss_low.ipynb), [InSAR](dvd_insar_low_off.ipynb), [EDM](example_synthetic_edm.ipynb) and [joint](dvd_joint_low.ipynb) datasets. We also included an example using real datasets on [Unimak Island](example_unimak_joint.ipynb).

## Add new datatype:

To include a new datatype you should create a new file and add it to the data folder. This file should contain a new class that inherit from the 'Data' class and that has the functions to initialize the attributes, adding the components belonging to the datatype and a function to derive the components from 3d displacements. For example, in the Insar class we defined the following functions:

```python
class Insar(Data):
    def __init__():
        ...
    def add_los(self, los):
        ...
    def from_model3d(self, func):
        ...
```

## Add new model:

To include a new model you should create a new file and add it to the source folder. This file should contain a new class that inherit from the 'Source' class and that has a function returning the names of the parameters in your model and a function that gives the implementation of your model and return the 3d displacement. If you want to use this model with data that has a temporal dependency you should include the function 'model_t' that implements a time-dependant model. As an option you can include additional functions that return tilt displacements with the function 'model_tilt' or if it has a temporal dependency 'model_tilt_t'. For example, here we show the required functions in our Mogi model:

```python
class Mogi(Source):
    def set_parnames(self):
        ...
    def model(self, params):
        ...
```

## Publications:

A list of publications where VMOD has been used:

- Grapenthin, R., Cheng, Y., Angarita, M., Tan, D., Meyer, F. J., Fee, D., & Wech, A. (2022). Return from Dormancy: Rapid inflation and seismic unrest driven by transcrustal magma transfer at Mt. Edgecumbe (L’úx Shaa) Volcano, Alaska. Geophysical Research Letters, 49(20), e2022GL099464. https://doi.org/10.1029/2022GL099464
- Grapenthin, R., Kyle, P., Aster, R. C., Angarita, M., Wilson, T., & Chaput, J. (2022). Deformation at the open-vent Erebus volcano, Antarctica, from more than 20 years of GNSS observations. Journal of Volcanology and Geothermal Research, 432, 107703. https://doi.org/10.1016/j.jvolgeores.2022.107703
- Graves, E. J., et al. "InSAR-observed surface deformation in New Mexico’s Permian Basin shows threats and opportunities presented by leaky injection wells." Scientific Reports 13.1 (2023): 17308. https://doi.org/10.1038/s41598-023-42696-9

