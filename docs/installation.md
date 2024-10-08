# Installation

As **FabMaMiCo** is a plugin for the automation tool [FabSim3](https://www.github.com/djgroen/FabSim3), **FabSim3** needs to be installed first.  
Once installed, you can install **FabMaMiCo** as a plugin for **FabSim3**.

## FabSim3

Please refer to the [FabSim3 documentation](https://fabsim3.readthedocs.io/en/latest/installation/) for the installation of **FabSim3**.

<!--
??? note
	Not all changes to the FabSim3 repository have been merged into the official repository yet, so you might want to follow the instructions below to install the forked version of FabSim3.

	1. Clone the FabSim3 repository:

		```sh
		git clone https://github.com/jomichaelis/FabSim3.git
		```

	2. To install all pip-packages automatically and to configure yml files, please type:
		```sh
		cd FabSim3
		python3 configure_fabsim.py
		```

	3. After installation process, the root FabSim3 directory should be added to both `PATH` and `PYTHONPATH` environment variables. The instruction to do that will be shown at the end of output of `python3 configure_fabsim.py` command.
		```bash
		Congratulation 🍻
		FabSim3 installation was successful ✔
		
		In order to use fabsim command anywhere in your PC, you need to update the PATH
		and PYTHONPATH environmental variables.
		
			export PATH=<install-path>/FabSim3/fabsim/bin:$PATH
			export PYTHONPATH=<install-path>/FabSim3:$PYTHONPATH

			export PATH=~/.local/bin:$PATH
		
		The last list is added because the required packages are installed with flag 
		"--user" which makes pip install packages in your your home instead instead 
		of system directory.


		Tip: To make these updates permanent, you can add the following command at the 
		end of your bash shell script which could be one of ['~/.bashrc', '~/.bash_profile', 
		'~/.zshrc', '~/.bash_aliases'] files, depends on your OS System.

		🛎 To load the new updates in PATH and PYTHONPATH you need to reload your bash shell 
		script, e.g., source ~/.bashrc, or lunch a new terminal.
		```

	4. To make the fabsim command available in your system, please restart the shell by opening a new terminal or just re-load your bash profile by `source` command.
-->

## FabMaMiCo

### Install
Install the FabMaMiCo plugin by running this FabSim3-command:
```sh
fabsim localhost install_plugin:FabMaMiCo
```

That's it. FabMaMiCo is now installed and ready to use.

### Verify Installation
To verify the successful installation, run the `mamico_test_plugin`-task of FabMaMiCo:
```sh
fabsim localhost mamico_test_plugin
```