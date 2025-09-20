import common

DO_SNAPSHOTS = True         # whether to automatically manage snapshots. recommended

RETAIN_DAILY = True         # whether to retain daily snapshots. recommended
RETAIN_DAILY_COUNT = 3      # how many daily snapshots to retain. mimimum 1 recommended

RETAIN_WEEKLY = True        # retain weekly snapshots
RETAIN_WEEKDAY = 0          # on which day should weekly snapshots be made. values 0-6, 0 == Monday, 6 == Sunday
RETAIN_WEEKLY_COUNT = 1     # how many weekly snapshots to retain

RETAIN_MONTHLY = True       # retain monthly snapshots
RETAIN_MONTHLY_DAY = 1      # the day of the month to do a monthly snapshot. starts from 1. values over 28 not supported
RETAIN_MONTHLY_COUNT = 1    # how many monthly snapshots to retain

RETAIN_QUARTERLY = True     # retain quarterly updates. will be done on Jan 1st, April 1st, Jul 1st and Oct 1st
RETAIN_QUARTERLY_COUNT = 1  # how many quarterly snapshots to retain

RETAIN_YEARLY = True        # whether to retain yearly snapshots
RETAIN_YEARLY_DAY = 1       # the day of the year to do a yearly snapshot. starts from 1. values over 365 not supported (leap years)
RETAIN_YEARLY_COUNT = 1     # how many yearly snapshots to retain

EXCLUDE_SNAPSHOTS = []      # add container ids for containers you don't want to snapshot. not recommended unless you also exclude them from updates


DO_UPDATE = True            # whether to run updates after a snapshot. recommended
ROLLBACK_ON_ERROR = True    # whether to rollback to the most recent snapshot if an error occours during the update process. ONLY use this when you have snapshots enabled
EXCLUDE_ROLLBACK = []       # containers to exclude from rolling back on error
UPDATE_TIMEOUT = 300        # timeout for the update command in seconds. default 300 seconds = 5 minutes
UPDATE_COMMANDS = {         # the update command to use for each distribution. these should not be modified
    common.OsType.ALPINE:   "apk update && apk upgrade",
    common.OsType.DEBIAN:   "apt update && apt upgrade -y && apt autoremove -y",
    common.OsType.UBUNTU:   "apt update && apt upgrade -y && apt autoremove -y",
    common.OsType.DEVUAN:   "apt update && apt upgrade -y && apt autoremove -y",
    common.OsType.ARCH:     "pacman -Syu && pacman -Rns $(pacman -Qdtq)",
    common.OsType.CENTOS:   "yum upgrade -y && yum autoremove -y",
    common.OsType.FEDORA:   "dnf upgrade --refresh -y && dnf autoremove -y",
    common.OsType.GENTOO:   "emerge --sync && emerge -uDN @world && emerge --depclean",
    common.OsType.NIXOS:    "nix-channel --update && nixos-rebuild switch --upgrade && nix-collect-garbage -d",
    common.OsType.OPENSUSE: "zypper refresh && zypper update -y && zypper remove --clean-deps $(zypper packages --unneeded --quiet)"
}
EXCLUDE_UPDATE = []         # list container ids you don't want to update
UPDATE_OVERRIDES = {        # map of container ids to custom update command overrides. the updater will use this command instead of the distribution default
#    100: "custom update command"
}