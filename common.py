import subprocess
import re
import datetime
from enum import Enum
from dateutil import parser

ct_regex = r"^(?P<ct>\d*)\s*(?P<state>\w*)\s*(?P<name>.*)\s*$"
ct_matcher = re.compile(ct_regex)

snapshot_regex = r".*-> (?P<tag>snapshot-(?P<cycle>\w*)-\d+_\d+)\s*(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*.*"
snapshot_matcher = re.compile(snapshot_regex)


class Arch(Enum):
    AMD64 = "amd64"
    ARM64 = "arm64"
    X_86  = "x86"


class OsType(Enum):
    DEBIAN = "debian"
    ALPINE = "alpine"
    UBUNTU = "ubuntu"
    ARCH = "archlinux"
    CENTOS = "centos"
    DEVUAN = "devuan"
    FEDORA = "fedora"
    GENTOO = "gentoo"
    NIXOS = "nixos"
    OPENSUSE = "opensuse"


class SnapshotType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class State(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    UNKNOWN = "unknown"
    SUSPENDED = "suspended"


class Snapshot:
    tag: str
    date: datetime.datetime
    type: SnapshotType
    age: datetime.timedelta


    def __init__(self, tag: str, date: datetime.datetime, type: SnapshotType):
        self.tag = tag
        self.date = date
        self.type = type
        self.age = datetime.datetime.now() - date


    def __str__(self) -> str:
        return f"{self.tag}  {self.date}  {self.type.value}  Age: {self.age}"


class Container():
    id: int
    arch: Arch
    cores: int
    features: str
    hostname: str
    memory: int
    os_type: OsType
    root_fs: str
    swap: int
    unprivileged: bool
    snapshots: list[Snapshot]
    state: State
    networks: dict[str, str]
    upgrade_safe: bool
    template: bool


    def _get_snapshots(self):
        output = subprocess.check_output(["pct", "listsnapshot", str(self.id)]).decode().split("\n")
        snapshots = []
        for snapshot in output[:-2]:
            try:
                match = snapshot_matcher.match(snapshot)
                if match is None:
                    print(f"Found unmanaged snapshot {snapshot} for CT {self.id}. Ignoring")
                    continue
                snapshots.append(Snapshot(
                    match.group("tag"),
                    parser.parse(match.group("datetime")),
                    SnapshotType(match.group("cycle"))
                ))
            except Exception as e:
                print(f"Error while trying to get snapshot from {self.id}:\nLine: {snapshot}\nError: {e}")
        return snapshots


    def __init__(self, id: int | str):
        self.id = int(id)
        self.networks = dict()
        self.template = False
        output = subprocess.check_output(["pct", "config", str(id)]).decode().split("\n")
        for line in output:
            match line.split(":")[0]:
                case "arch": self.arch = Arch(line[6:])
                case "ostype": self.os_type = OsType(line[8:])
                case "features": self.features = line[10:]
                case "memory": self.memory = int(line[8:])
                case "rootfs": self.root_fs = line[8:]
                case "cores": self.cores = int(line[7:])
                case "swap": self.swap = int(line[6:])
                case "hostname": self.hostname = line[9:]
                case "unprivileged": self.unprivileged = bool(line[14:])
                case "template": self.template = bool(line[10:])
                case _:
                    if line.startswith("net"):
                        split = line.split(" ")
                        self.networks[split[0][:-1]] = split[1]
        output = subprocess.check_output(["pct", "status", str(id)]).decode()
        self.state = State(output[8:-1])
        self.snapshots = self._get_snapshots()
        # sort snapshots from new to old. required for cleanup
        self.snapshots.sort(key=lambda snapshot: snapshot.date, reverse=True)
        self.upgrade_safe = True
        print(f"Parsed information for CT {self.id}")


    def __str__(self):
        return f"""id: {self.id}
state: {self.state}
arch: {self.arch}
cores: {self.cores}
features: {self.features}
hostname: {self.hostname}
memory: {self.memory}
{"\n".join(map(lambda key: f"{key}: {self.networks[key]}", self.networks))}
ostype: {self.os_type}
rootfs: {self.root_fs}
swap: {self.swap}
unprivileged: {self.unprivileged}
snapshots: {self.snapshots}"""


def get_containers() -> list[Container]:
    output = subprocess.check_output(["pct", "list"]).decode().split("\n")
    containers = []
    for line in output[1:-1]:
        try:
            match = ct_matcher.match(line)
            assert(match is not None)
            containers.append(Container(match.group("ct")))
        except Exception as e:
            print(f"Error while trying to get container id:\nLine: {line}\nError: {e}")
    return containers


def create_snapshot(container: Container, type: SnapshotType):
    now = datetime.datetime.now()
    tag = f"snapshot-{type.value}-{now.strftime('%Y%m%d_%H%M%S')}"
    subprocess.check_call(["pct", "snapshot", str(container.id), tag, "--description", "Managed by Snapmox"])
    container.snapshots.append(Snapshot(tag, now, type))
    print(f"Created {type.value} snapshot for CT {container.id}")


def snapshot_exists(container: Container) -> bool:
    # Returns True if the container already has a managed snapshot for today
    # Used to prevent duplicate snapshots if the script is run multiple times
    now = datetime.datetime.now()
    for snapshot in container.snapshots:
        if snapshot.date.year == now.year and snapshot.date.month == now.month and snapshot.date.day == now.day:
            return True
    return False


def remove_snapshot(container: Container, snapshot: Snapshot) -> None:
    try:
        subprocess.check_call(["pct", "delsnapshot", str(container.id), snapshot.tag])
        print(f"Removed snapshot {snapshot.tag} for CT {container.id}")
    except Exception as e:
        print(f"An error occoured trying to remove snapshot {snapshot.tag} for CT {container.id}:\n{e}")


def rollback(container: Container) -> None:
    try:
        subprocess.check_call(["pct", "rollback", str(container.id), container.snapshots[-1].tag, "--start", "true"])
        print(f"Rolled CT {container.id} back to {container.snapshots[-1].tag}")
    except Exception as e:
        print(f"An error occoured trying to roll back CT {container.id}:\n{e}")