import config
import common
from datetime import datetime

def run(containers: list[common.Container]) -> None:
    print("Starting snapshot creation")
    for container in containers:
        now = datetime.now()
        if container.id in config.EXCLUDE_SNAPSHOTS:
            print(f"Skipping snapshot creation for CT {container.id} due to exclude list")
            continue
        if common.snapshot_exists(container):
            print(f"A managed snapshot of CT {container.id} already exists today. Skipping creation")
            container.upgrade_safe = False      # skip upgrade to prevent data loss on error
            continue
        if config.RETAIN_YEARLY and config.RETAIN_YEARLY_DAY == now.timetuple().tm_yday:
            common.create_snapshot(container, common.SnapshotType.YEARLY)
        elif config.RETAIN_QUARTERLY and now.day == 1 and (now.month == 1 or now.month == 4 or now.month == 7 or now.month == 10):
            common.create_snapshot(container, common.SnapshotType.QUARTERLY)
        elif config.RETAIN_MONTHLY and config.RETAIN_MONTHLY_DAY == now.day:
            common.create_snapshot(container, common.SnapshotType.MONTHLY)
        elif config.RETAIN_WEEKLY and config.RETAIN_WEEKDAY == now.weekday():
            common.create_snapshot(container, common.SnapshotType.WEEKLY)
        elif config.RETAIN_DAILY:
            common.create_snapshot(container, common.SnapshotType.DAILY)
        else:
            print("Skipping snapshot creation. THIS IS NOT RECOMMENDED!!!")
    print("Done creating snapshots")