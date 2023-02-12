
# Quickstart your Windows OpenSSH client via this launcher
Want to use OpenSSH sessions on your Windows desktop? Follow these simple steps:
- Install the package
- Create a `.winssh` folder in your homefolder
- Add a file `winssh-launcher.ini` and add your sessions

# Example winssh-laucher.ini
```
[DEFAULT]
ssh.port = 42

[diskstation]
host = 192.168.1.4
port = 22

[host-01.example.com]
group = home

```

The default SSH port is `42`, meaning every session you add is expected to listen on port 42. `diskstation` is an exception; this server listens on port `22` and uses ip `192.168.1.4`. Server `host-01.example.com` listens on port `42`

Sessions are added to the default group. You can add a session to a group via the `group` keyword. This allows for groups, meaning you can filter the SSH connections by the group label

# Using SSH keys
```
[DEFAULTS]
ssh.key.installdir = C:\Users\yourusernamehere\AppData\Local\ssh
ssh.key.pem.filenames = bastbnl-somevps.pem
ssh.port = 42

[diskstation]
host = 192.168.1.4
port = 22

[host-01.example.com]
group = home

```

`ssh.key.pem.filenames` contains a comma-separated list of PEM-formatted SSH private keys. The launcher can load these keys into the ssh-agent, when the Windows service is activated. You can list keys using absolute path or relative, in which case you need to add `ssh.key.installdir`, as this folder contains the folder that holds the private keys

Private key loading only works when the Windows OpenSSH Authentication Agent service is active

# Build an MSI
```
- pip install cx_freeze
- python freeze.py bdist_msi

```

The msi will be in `dist/winssh-launcher-<version>.win64.msi`. Install it
