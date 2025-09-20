import common
import config

def run(containers: list[common.Container]) -> None:
    print("Starting snapshot cleanup")
    
    for container in containers:
        print(f"Cleaning snapshots for CT {container.id}")

        daily_count = 0
        weekly_count = 0
        monthly_count = 0
        quarterly_count = 0
        yearly_count = 0

        # this procedure presumes snapshots are sorted by ascending age
        # sorting is done on container creation
        for snapshot in container.snapshots:
            match snapshot.type:
                case common.SnapshotType.DAILY:
                    daily_count += 1
                    if daily_count > config.RETAIN_DAILY_COUNT:
                        common.remove_snapshot(container, snapshot)
                case common.SnapshotType.WEEKLY:
                    weekly_count += 1
                    if weekly_count > config.RETAIN_WEEKLY_COUNT:
                        common.remove_snapshot(container, snapshot)
                case common.SnapshotType.MONTHLY:
                    monthly_count += 1
                    if monthly_count > config.RETAIN_MONTHLY_COUNT:
                        common.remove_snapshot(container, snapshot)
                case common.SnapshotType.QUARTERLY:
                    quarterly_count += 1
                    if quarterly_count > config.RETAIN_QUARTERLY_COUNT:
                        common.remove_snapshot(container, snapshot)
                case common.SnapshotType.YEARLY:
                    yearly_count += 1
                    if yearly_count > config.RETAIN_YEARLY_COUNT:
                        common.remove_snapshot(container, snapshot)
        print(f"Done cleaning snapshots for CT {container.id}")

    print("Done cleaning snapshots")