from pathlib import Path
from subprocess import CalledProcessError

from cybulde.utils.utils import get_logger, run_shell_command


DATA_UTILS_LOGGER = get_logger(Path(__file__).name)


def is_dvc_initialized() -> bool:
    return (Path().cwd() / ".dvc").exists()


def initialize_dvc() -> None:
    if is_dvc_initialized():
        DATA_UTILS_LOGGER.info("DVC is already initialized")
        return

    DATA_UTILS_LOGGER.info("Initializing DVC")
    run_shell_command("dvc init")
    run_shell_command("dvc config core.analytics false") # we dont want dvc to collect any analytics from reposetory
    run_shell_command("dvc config core.autostage true") # cuz if we update something in the data we want dvc to automaticaly stage it
    run_shell_command("git add .dvc") # for adding the .dvc dir to the reposetory
    run_shell_command("git commit -nm 'Initialized DVC'") # commite the changes


def initialize_dvc_storage(dvc_remote_name: str, dvc_remote_url: str) -> None:
    if not run_shell_command("dvc remote list"): # to check if dvc storage was initialized or not
        DATA_UTILS_LOGGER.info("Initializing DVC storage...")
        run_shell_command(f"dvc remote add -d {dvc_remote_name} {dvc_remote_url}") # for store the data
        run_shell_command("git add .dvc/config") # the above command is ganna modifay the .dvc/config so we nead to add it to github storage
        run_shell_command(f"git commit -nm 'Configured remote storage at: {dvc_remote_url}'") # commit changes
    else:
        DATA_UTILS_LOGGER.info("DVC storage was already initialized...")