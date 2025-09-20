import common
import config
import create_snapshots
import remove_snapshots
import update
from datetime import datetime

start = datetime.now()

print("Gathering containers...")
containers = common.get_containers()
print("Done gathering containers")

if config.DO_SNAPSHOTS:
    create_snapshots.run(containers)
    remove_snapshots.run(containers)

if config.DO_UPDATE:
    update.run(containers)

print(f"Execution finished. Time taken: {datetime.now() - start}")