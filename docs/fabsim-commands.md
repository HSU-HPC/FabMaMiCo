# Fabsim Commands

FabSim3 offers a variety of commands to interact with remote machines and to manage simulation campaigns.  
Each plugin can provide additional commands.  

A FabSim3 command is usually structured as follows:
```sh
fabsim <machine> <task>:<task-arguments>
```

The following list provides an overview of the most important commands.


#### Local FabSim3 commands

```sh
fabsim -l/--list tasks
# Prints the list of available tasks (FabSim3 API, [...FabSim plugins])
```

```sh
fabsim -l/--list machines
# Prints the list of available remote machines.
```

```sh
fabsim localhost avail_plugin
# Prints the list of available plugins on localhost.
```

```sh
fabsim localhost install_plugin:<plugin-name>
# Installs the specified plugin on localhost.
```

```sh
fabsim localhost update_plugin:<plugin-name>
# Updates the specified plugin on localhost (pulls latest version from the repository).
```

```sh
fabsim localhost remove_plugin:<plugin_name>
# Removes the specified plugin from the remote machine.
```


#### Remote FabSim3 commands

```sh
fabsim <remote-machine> machine_config_info
# Prints the configuration information for the specified remote machine.
# Both configs from 'machines.yml' and 'machines_user.yml' are printed.
```

```sh
fabsim <remote-machine> stat
# Prints the status of the job scheduler on the remote machine.
# [as configured in machines.yml]
```

```sh
fabsim <remote-machine> wait_complete:jobID=<jobID>
# Waits until the job with the specified jobID is completed on the remote machine.
# jmToDo: check if this is working
```

```sh
fabsim <remote-machine> cancel_job:jobID=<jobID>
# Cancels the job with the specified jobID on the remote machine.
# [as configured in machines.yml]
```

```sh
fabsim <remote-machine> put_results
# Copies the results from localhost to the remote machine.
# This is not intended for normal use.
```

```sh
fabsim <remote-machine> fetch_results
# Copies the results from the remote machine to localhost.
```

```sh
fabsim <remote-machine> clear_results
# Removes the results from the remote machine via `rm -rf $job_results_contents`.
```

```sh
fabsim <remote-machine> fetch_configs
# Fetches the config-files from the remote machine to localhost.
```


#### Setup Tasks
```sh
fabsim <remote-machine> setup_ssh_keys[:password=<password>]
# Sets up SSH keys for passwordless login to the remote machine.
# If `.ssh/id_rsa.pub` exists, it will be copied to the remote machine.
# If not, a new key pair will be generated and copied to the remote machine.
# A password can be provided as an optional argument.
```


#### Internal FabSim3 Tasks
```sh
fabsim <remote-machine> setup_fabsim_dirs
# Creates the following dirs on the remote machine:
# - $config_path
# - $results_path
# - $scripts_path
## Used in put_configs()
```

```sh
fabsim <remote-machine> clean_fabsim_dirs
# Recursively removes the following dirs on the remote machine:
# - $config_path
# - $results_path
# - $scripts_path
## Used in put_configs()
```

#### more
- ensemble2campaign
- campaign2ensemble
- install_packages (installs packages)
- install_app (locally install an app e.g. QCG-PilotJob, transfer it afterwards, launch install-script job)