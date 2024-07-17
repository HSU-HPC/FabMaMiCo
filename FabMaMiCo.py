import os

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *

from fabsim.deploy.templates import template

from plugins.FabMaMiCo.scripts.main_configuration import MainConfiguration
from plugins.FabMaMiCo.scripts.setup import Setup

# Add local script, blackbox and template path.
add_local_paths("FabMaMiCo")

FabMaMiCo_plugin_path = get_plugin_path("FabMaMiCo")


def populate_env_templates():
    """
    Populate the environment variable templates.
    """
    data = {}
    data["mamico_dir"] = template(env.mamico_dir_template)
    # ... add more templates here (if necessary)
    update_environment(data)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_install(config: str, **args):
    """
    Transfer the MaMiCo source code to the remote machine and compile it with all its dependencies.
    This task downloads the MaMiCo source code from the MaMiCo repository and optionally ls1-mardyn.
    It checks out the given branch/commit/tag and transfers the code to the remote machine.
    It then compiles the code on the remote machine, either on the login node or on a compute node.
    """
    populate_env_templates()
    with_config(config)
    update_environment(args)
    # Read configuration
    configuration = MainConfiguration(FabMaMiCo_plugin_path, config)
    # Setup the MaMiCo according to the configuration
    setup = Setup(FabMaMiCo_plugin_path, config, configuration)
    # Prepare source codes locally
    # This might also update the configuration parameters: mamico_branch_tag_commit, ls1_branch_tag_commit
    setup.prepare_local()
    checksum = configuration.generate_checksum()
    env.update({ "mamico_checksum": checksum })
    # Prepare source codes remotely
    setup.prepare_remote()
    # Compile the code
    setup.compile(**args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_run(config: str, **args):
    """
    Run a single MaMiCo simulation.
    This task assumes that there exists a MaMiCo executable already.
    It generates the batch script and submits the job.
    """
    populate_env_templates()
    with_config(config)
    update_environment(args)
    # Read configuration
    configuration = MainConfiguration(FabMaMiCo_plugin_path, config)
    # Setup the MaMiCo according to the configuration
    setup = Setup(FabMaMiCo_plugin_path, config, configuration)
    # Prepare source codes locally
    # This might also update the configuration parameters: mamico_branch_tag_commit, ls1_branch_tag_commit
    setup.prepare_local()
    checksum = configuration.generate_checksum()
    env.update({ "mamico_checksum": checksum })

    # Copy the configuration files to the remote machine
    rsync_project(
        remote_dir=os.path.join(env.mamico_dir, env.mamico_checksum, 'build'),
        local_dir=os.path.join(FabMaMiCo_plugin_path, 'config_files', config, 'simulation')
    )
    # set run_command
    env["run_command"] = f"mpirun -np {env.get('cores', 1)}" if configuration.configs['MaMiCo'].get('BUILD_WITH_MPI', False) else ""
    # submit the job
    job(dict(script='run', job_wall_time='0:15:0'), args)


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_all(config: str, **args):
    """
    Run a single MaMiCo simulation.
    This task makes sure that the MaMiCo code is installed and compiled on the remote machine.
    It triggers both the `mamico_install` and `mamico_run` tasks.
    """
    mamico_install(config, **args)
    # wait


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_list_installations(**args):
    """
    List all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    print_box(
        f"Please wait until the MaMiCo installations on {env.host} are listed.\n"\
        f"Note that the list contains installations at {env.mamico_dir} only.",
        title=f"Listing MaMiCo installations on {env.host}",
        color="pink1"
    )
    # Check for all md5 checksum folders that contain a build folder with a couette executable
    installations = run(
        f"find {env.mamico_dir} -type d \\"\
        f"( -exec test -d {{}}/build \; -a -exec test -f {{}}/build/couette \; \) "\
        f"-print",
        capture=True
    )
    numInstallations = len(installations.split())
    print_box(
        "\n".join(installations.split()),
        title=f"Found {numInstallations} installation{'s' if numInstallations != 1 else ''} on {env.host}",
        color="green"
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_remove_installation(checksum: str, **args):
    """
    Remove a specific MaMiCo installation directory on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    installations = run(f"ls {env.mamico_dir}", capture=True)
    installations = installations.split()
    if not checksum in installations:
        print_box(
            f"MaMiCo installation {checksum} does not exist on {env.host}.\n"\
            f"There is no directory to be removed.",
            title=f"MaMiCo installation not found!",
            color="red",
        )
        sys. exit(1)
    print_box(
        f"Please wait until the MaMiCo installation {checksum} is removed.",
        title=f"Cleaning MaMiCo installation on {env.host}",
        color="pink1",
    )
    # Remove directory recursively
    mamico_dir = os.path.join(env.mamico_dir, checksum)
    run(f"rm -rf {mamico_dir}")
    print_box(
        f"{mamico_dir} was removed from {env.host}.",
        title="Clean up successful",
        border_style="green",
    )


@task
@load_plugin_env_vars("FabMaMiCo")
def mamico_remove_all_installations(**args):
    """
    Remove all MaMiCo installations on the remote machine.
    """
    populate_env_templates()
    update_environment(args)
    print_box(
        f"Please wait until all MaMiCo installations on {env.host} are removed.\n"\
        f"Note that only installations at {env.mamico_dir} are removed.",
        title="Cleaning MaMiCo installations",
        color="pink1"
    )
    # Remove all directories recursively
    run(f"rm -rf {env.mamico_dir}/*")
    print_box(
        f"MaMiCo installations were successfully removed from {env.host}.",
        title="Clean up successful!",
        color="green",
    )
