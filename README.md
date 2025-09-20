# Snapmox

A simple and configurable tool for automating Proxmox LXC snapshots and updates.

## Features

- This tool has highly configurable options to automatically create snapshots and update LXC containers
- There are 5 snapshot cycles: `YEARLY, QUARTERLY, MONTHLY, WEEKLY` and `DAILY`
- You can configure how many snapshots should be retained for each cycle
- Manually created snapshots that don't match the managed pattern will not be removed or taken into account in any way
- You can run automatic updates in the containers which are executed immediately after the snapshots are created
- This way, if anything goes wrong with the update you have an immediate snapshot to fall back on
    - You can also configure automatic rollbacks when an error occours during an update
- You can also configure containers which are excluded from snapshots/updates if you prefer to manage them manually
- The update command is configurable per container and uses the default command for the distribution if no custom command is configured

## Installation

1. Clone or copy the repository to `/etc/pve/snapmox`. This directory is synced between Proxmox nodes automatically so you don't need to manually sync the config
2. You don't need any additional Python modules, the tool only uses the Python standard library
3. Adjust `/etc/pve/snapmox/config.py` to your liking
4. Add a cron job with `crontab -e` on each node in your cluster
    - Make sure the script has enough time to complete before the nex day begins. Otherwise there might be unintended behavior with snapshots not being created
    - I would recommend running the script each day early in the morning, e.g. `30 5 * * *` or `every day at 5:30 a.m`
    - The `pct` and `python3` binaries must be found in the `PATH` for the cronjob. You can achieve this by prepending `PATH=/bin:/usr/sbin` to your command
    - Files in `/etc/pve` cannot have an executable flag. To circumvent this, call the script indirectly with `python3 /path/to/script`
    - An example job: `30 5 * * * PATH=/bin:/usr/sbin python3 /etc/pve/snapmox/run.py`
5. (Optional) Configure `postfix` to be able to send mails to your monitoring inbox (if you have one)
    - The config is highly dependent on your specific email setup so I will not provide a guide here
    - This way you will receive the full log into your mailbox whenever the script runs

## Configuration

The default configuration should suffice for most users. The options are documented in the `config.py` file