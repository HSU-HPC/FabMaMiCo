# File Structure

By default, FabSim uses two different machine configuration files:

- machine-specific configuration file: `FabSim3/fabsim/deploy/machines.yml`
    - This file is part of the *FabSim3* repository
    - It contains the default settings like remote url, job scheduler-dependent commands, number of nodes, etc.
- user-specific configuration file: `FabSim3/fabsim/deploy/machines_user.yml`
    - This file is not part of *FabSim3* repository
    - It contains user-specific settings like username, partition, account, etc.

```
.
├─ fabsim/
│  └─ deploy/
│     ├─ machines.yml
│     ├─ machines_user.yml
│     ├─ (machines_user_example.yml)
│     └─ (machines_user_backup.yml)
├─ plugins/
│  └─ FabMaMiCo/
│     └─ (machines_FabMaMiCo_user_example.yml)
```