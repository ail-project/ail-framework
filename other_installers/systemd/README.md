# Running AIL with systemd

The service uses AIL's launcher to start the databases, workers, and Flask. The workers run in the `Script_AIL` GNU Screen session, with one window per module. The service instance name identifies the Linux account that owns the AIL installation and its Screen sessions.

Install AIL and its dependencies first, using a dedicated unprivileged account with access to the checkout and write access to AIL's runtime files. The examples use the account `ail` and a checkout at `/opt/ail-framework`. If AIL is already running, stop it with `bash bin/LAUNCH.sh -k` as the installation owner before switching to systemd. Use one instance per set of AIL ports.

From the checkout, install the unit.

```bash
sudo install -m 0644 other_installers/systemd/ail@.service /etc/systemd/system/ail@.service
```

For a checkout outside `/opt/ail-framework`, run `sudo systemctl edit ail@ail.service` and set its absolute path.

```ini
[Service]
WorkingDirectory=/path/to/ail-framework
```

Reload systemd and enable the service. Substitute your installation account for `ail` after the `@` in each command.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ail@ail.service
sudo systemctl status ail@ail.service
```

## Attach to the module console

Screen sockets are private to the service account. Run Screen as that account with the service's socket directory. In the example, the final `ail` in `/run/ail-screen-ail` is the account name.

```bash
sudo -u ail env SCREENDIR=/run/ail-screen-ail screen -ls
sudo -u ail env SCREENDIR=/run/ail-screen-ail screen -r Script_AIL
```

Use **Ctrl+A**, then **"** to list the module windows. Use **Ctrl+A**, then **D** to detach and leave AIL running. To share an already attached session, use `screen -x Script_AIL` with the same account and socket directory. You can attach to `Flask_AIL` the same way.

## Stop, restart, and diagnose

```bash
sudo systemctl stop ail@ail.service
sudo systemctl restart ail@ail.service
sudo journalctl -u ail@ail.service -b
```

The service runs the launcher's database shutdown and lets systemd clean up any remaining processes in the service. Systemd reports `active (exited)` after startup because the launcher exits while Screen keeps the processes running. Check individual module output from Screen. The journal records the launcher output and startup checks.

The service skips the launcher's automatic update on startup. Run updates deliberately as the installation account using the repository's update instructions.
