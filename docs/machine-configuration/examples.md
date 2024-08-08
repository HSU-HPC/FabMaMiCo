# Concrete examples of machine configuration

ToDo!

#### `machines.yml`

=== "HSUper"

    ```yaml
    hsuper:
        remote: "hsuper-login.hsu-hh.de"
        home_path_template: "/beegfs/home/m/$username"
        batch_header: slurm-hsuper
        job_dispatch: "sbatch"
        stat: "squeue -u $username --Format=jobid,state,account,timeleft,timeused,username --noheader"
        cancel_job_command: "scancel"
        prevent_results_overwrite: "warn_only"
        modules:
            mamico: ["load python"]
    ```

=== "Cosma"

    ```yaml
    cosma:
        remote: cosma
        home_path_template: "/cosma/home/do009/$username"
        batch_header: slurm-cosma
        job_dispatch: "sbatch"
        cores: 1
        job_wall_time: "0-0:01:00"
        manual_ssh: true
    ```

=== "Sofja"

    ```yaml
    todo: true
    # NO INTERNET CONNECTION (https://wasd.urz.uni-magdeburg.de/jschulen/urz_hpc/hpc21/)
    ```

=== "Ants"

    ```yaml
    todo: true
    ```

=== "Minicluster"

    ```yaml
    todo: true
    ```

=== "Fritz"

    ```yaml
    todo: true
    ```

=== "Alex"

    ```yaml
    todo: true
    ```
----

#### `machines_user.yml`

=== "default"

    ```yaml
    default:
        local_results: "/home/jo/repos/FabSim3/results"
        local_configs: "/home/jo/repos/FabSim3/config_files"
    ```

=== "HSUper"

    ```yaml
    username: "michaelj"
    ```

=== "Cosma"

    ```yaml
    username: "dc-mich3"
    ```

=== "Sofja"

    ```yaml
    username: "qeqe81qu"
    ```

=== "Ants"

    ```yaml
    username: "qeqe81qu"
    ```

=== "Minicluster"

    ```yaml
    username: "jo"
    ```

=== "Fritz"

    ```yaml
    todo: true
    ```

=== "Alex"

    ```yaml
    todo: true
    ```
----