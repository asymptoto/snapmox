import common
import config
import subprocess


def run(containers: list[common.Container]) -> None:
    print("Starting updates")
    for container in containers:
        try:
            if container.id in config.EXCLUDE_UPDATE:
                print(f"Skipping updates for CT {container.id} due to exclusion list")
                continue
            if container.state != common.State.RUNNING:
                print(f"CT {container.id} is not running. Skipping updates")
                continue
            if not container.upgrade_safe:
                print(f"Skipping upgrade for CT {container.id} due to unsafe upgrade state")
                continue
            update_command = None
            if container.id in config.UPDATE_OVERRIDES:
                update_command = config.UPDATE_OVERRIDES[container.id]
            elif container.os_type in config.UPDATE_COMMANDS:
                update_command = config.UPDATE_COMMANDS[container.os_type]
            else:
                print(f"No update command configured for CT {container.id} with OS type {container.os_type}. Skipping update")
                continue
            
            try:
                print(f"Updating CT {container.id}...")
                output = subprocess.check_output(["pct", "exec", str(container.id), "--", "sh", "-c", update_command], timeout=config.UPDATE_TIMEOUT, stderr=subprocess.STDOUT).decode()
                print(output)
                print(f"Done updating CT {container.id}")
            except Exception as e:
                print(f"An error has occoured during the update of CT {container.id}:\n{e}")
                if config.ROLLBACK_ON_ERROR and container.id not in config.EXCLUDE_ROLLBACK:
                    common.rollback(container)
        except Exception as e:
            print(f"An error occoured while trying to update CT {container.id}: {e}")
    print("Done with updates")