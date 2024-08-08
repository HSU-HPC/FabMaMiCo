# SSH Multiplexing

Some remote machines might require a passkey-password authentication.
This means that every connection demands both a matching ssh-key-authentication and a separate password input afterwards to login successfully.

This might become an issue, especially since FabSim is designed to establish multiple ssh connections sequentially, however all of them require a separate authentication procedure.
It is not feasible to enter the password for every single command like `rsync`, `scp`, etc.

To overcome this issue, we can use the SSH multiplexing feature, which is explained in detail in the (FabSim3 documentation)[https://fabsim3.readthedocs.io/en/latest/multiplex_setup/].

## SSH Multiplexing

SSH multiplexing allows users to reuse an existing connection to a remote host, so they don't have to authenticate again.

To enable SSH multiplexing, add the following lines to your `~/.ssh/config` file:

```sh
Host cosma
    User    <username>
    HostName <hostname-url>
    IdentityFile ~/.ssh/id_rsa
    ControlPath ~/.ssh/controlmasters/%r@%h:%p
    ControlMaster auto
    ControlPersist yes
```

This will create a master connection to the remote host, and all subsequent connections will use this master connection.

The `ControlPersist` option specifies how long the master connection should be kept alive after the last connection is closed.
The default value is `no`, which means the master connection will be closed as soon as the last connection is closed.
The option `yes` keeps the master connection alive infinitely, but time intervals can also be defined: `10m`, `30m`, `1h`, etc.

The directory `~/.ssh/controlmasters/` must exist, otherwise please create it:
```sh
mkdir -p ~/.ssh/controlmasters/
```

## Usage
Once this is set up, connect to the remote machine with:

```sh
ssh cosma
```

After submitting the password, the master connection will be established and all subsequent connections will use this master connection.

Is is important that in the `machines.yml` file, the parameter `remote` is set to the `Host` name in the `~/.ssh/config` file, not the URL of the remote host.

```yaml
cosma:
  remote_host: cosma # not: login8.cosma.dur.ac.uk!!!
```

## Useful Commands

```sh
ssh -O check cosma # check if the master connection is still alive
ssh -O stop cosma  # stop the master connection
```