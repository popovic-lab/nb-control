# nb-control - Narrow Band System Control Modules

This repository contains the modules and scripts for controlling the narrow band system scan procedure. 

The direct-conversion (DC) receiver control relies on the manufacturer's Linear Lab Tools for Python 2.7. 

To maintain compatibility, the rest of the modules are also on Python 2.7. 

Modules were written for Windows OS.


# Dependencies: 

# Third Party Software:

* Anaconda package with Python 2.7
* Source-code editor (Python) of choice, suggest Visual Studio Code (VSCode)

## Third Party Modules required (conda install) - Already included in the conda virtual environment:

* glob2
* matplotlib
* natsort
* numpy
* pandas
* pathlib
* pyserial
* scipy
* seaborn
* timeit
* tqdm

(the environment includes other packages that may not be used in the current version of the modules)

# Installation Instructions

## 1.0) Install Anaconda

Instructions can be found on:

https://docs.anaconda.com/anaconda/install/

Current Anaconda builds use Python 3 by default and it is recommended to install the latest version. 

A virtual environment using Python 2.7 will be used.

### 1.1) Environment

These modules use Python 2.7 with a conda virtual environment whose packages list is stored in the `narrowband.yml` file, found in the `env/` folder.

Open the Anaconda Prompt with administrator rights.

To navigate to the correct folder:

``` > cd/```

``` > cd Your-Path-Here/nb-control/env/```

To create/install the specified environment:

``` conda env create -f narrowband.yml ```

If you perform changes afterwards, to export a modified environment with only the user selected packages:  
``` conda env export --from-history > narrowband.yml ```

## 2.0) Install Code Editor (Visual Studio Code preferred)

https://code.visualstudio.com/docs/setup/setup-overview

After installation, the Python extension should be installed.

https://code.visualstudio.com/docs/editor/extension-marketplace

https://marketplace.visualstudio.com/items?itemName=ms-python.python

### 2.1) Powershell (optional)

VSCode also suggests installing the latest Powershell Terminal (as of this writing, v7.1):

https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell?view=powershell-7.1

Afterwards, open Anaconda Prompt with administrator rights and perform:

```conda init```

Or else open Anaconda Powershell Prompt with administrator rights and perform:

```conda init powershell```

This should configure terminals such as Powershell to activate conda environments. More details on environments and terminals with VSCode:

https://code.visualstudio.com/docs/python/environments#_environments-and-terminal-windows

https://code.visualstudio.com/docs/editor/integrated-terminal#_configuration

Some further reading on the Anaconda with Python interaction:

https://docs.anaconda.com/anaconda/user-guide/tasks/integration/python-vsc/

https://code.visualstudio.com/docs/python/environments

Upon first use with a Python file, VSCode should ask you which interpreter and conda environment to use and you should select `Python 2.7.x 64-bit : ('narrowband' : conda)`.

Further reading on Python with VSCode:

https://code.visualstudio.com/docs/python/python-tutorial

## 3.0) Install Linear Lab Tools (64-bit) for Python

DC receiver control requires this package from Linear Technology (now part of Analog Devices).

The modules expect the installation path to be:

```'%UserProfile%/Documents/linear_technology/linear_lab_tools64/'```

https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-development-platforms/linearlab-tools.html

https://www.analog.com/media/en/engineering-tools/design-tools/linearlabtools_python_install_instructions.pdf

# Use with VSCode

Open a new workspace and the folder `nb-control/`. Then open the file `narrow_band_system_script.py`.

The script should be configured in the `MeasParameters` dictionary and the `Phantom details - Reinforcing values` sections. 

The script should be manually edited after each mesurement, by uncommenting the appropriate lines and commenting (with a `#`) the other lines in the calibration rounds and actual measurements lines.

Before running the script, the USB hub should be connected between computer and narrowband system. The latter also needs to be powered on (**ATTENTION** to the voltages!).

To run the file in terminal, either click on the play button in the top-right side of the editor or
right-click anywhere in the editor window and select 'Run Python file in terminal'.

Please refer to the Narrowband_System_User_Guide.pdf document for more details on the hardware and measurement procedure.




