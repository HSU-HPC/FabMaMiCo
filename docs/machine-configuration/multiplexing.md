# SSH Multiplexing

COSMA supercomputer, just to name one example, requires a passkey-password authentication.
This means that every connection demands both a matching ssh-key-authentication and a separate password input afterwards to login.

This might become an issue, especially since FabSim is designed to run multiple tasks sequentially, however all of them require a separate authentication procedure.
It is not feasible to enter the password for every single task like `rsync`, `ssh`, `scp`, etc.

To overcome this issue, we can use the SSH multiplexing feature.

## SSH Multiplexing

SSH multiplexing allows you to reuse an existing connection to a remote host, so you don't have to authenticate again.

To enable SSH multiplexing, you need to add the following lines to your `~/.ssh/config` file:

```sh
Host cosma
    User    <username>
    HostName login8.cosma.dur.ac.uk
    IdentityFile ~/.ssh/id_rsa
    ControlPath ~/.ssh/controlmasters/%r@%h:%p
    ControlMaster auto
    ControlPersist 10m </ 30m / 1h / yes>
```

This will create a master connection to the remote host, and all subsequent connections will use this master connection.

The `ControlPersist` option specifies how long the master connection should be kept alive after the last connection is closed.
The default value is `no`, which means the master connection will be closed as soon as the last connection is closed.
You can set it to `yes` to keep the master connection alive indefinitely, or you can specify a time interval like `10m`, `30m`, `1h`, etc.

Make sure, the directory `~/.ssh/controlmasters/` exists, otherwise create it.
```sh
mkdir -p ~/.ssh/controlmasters/
```

## Usage
Once this is set up, you can connect to cosma with:

```sh
ssh cosma
```

After submitting the password, the master connection will be established and all subsequent connections will use this master connection.

Is is important that in the `machines.yml` file, the `remote` is set to the `Host` name in the `~/.ssh/config` file, not the URL of the remote host.

```yaml
cosma:
  remote_host: cosma # not: login8.cosma.dur.ac.uk!!!
```

## Useful Commands

```sh
ssh -O check cosma # check if the master connection is still alive
ssh -O stop cosma  # stop the master connection
```
