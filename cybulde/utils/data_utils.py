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
    run_shell_command("dvc config core.analytics false")  # we dont want dvc to collect any analytics from reposetory
    run_shell_command(
        "dvc config core.autostage true"
    )  # cuz if we update something in the data we want dvc to automaticaly stage it
    run_shell_command("git add .dvc")  # for adding the .dvc dir to the reposetory
    run_shell_command("git commit -nm 'Initialized DVC'")  # commite the changes


def initialize_dvc_storage(dvc_remote_name: str, dvc_remote_url: str) -> None:
    if not run_shell_command("dvc remote list"):  # to check if dvc storage was initialized or not
        DATA_UTILS_LOGGER.info("Initializing DVC storage...")
        run_shell_command(f"dvc remote add -d {dvc_remote_name} {dvc_remote_url}")  # for store the data
        run_shell_command(
            "git add .dvc/config"
        )  # the above command is ganna modifay the .dvc/config so we nead to add it to github storage
        run_shell_command(f"git commit -nm 'Configured remote storage at: {dvc_remote_url}'")  # commit changes
    else:
        DATA_UTILS_LOGGER.info("DVC storage was already initialized...")


def commit_to_dvc(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    current_version = run_shell_command("git tag --list | sort -t v -k 2 -g | tail -1 | sed 's/v//'").strip()
    if not current_version:
        current_version = "0"
    next_version = f"v{int(current_version)+1}"
    run_shell_command(f"dvc add {dvc_raw_data_folder}")
    run_shell_command("git add .")
    run_shell_command(f"git commit -nm 'Updated version of the data from v{current_version} to {next_version}'")
    run_shell_command(
        f"git tag -a {next_version} -m 'Data version {next_version}'"
    )  # tagging the version on github repository
    run_shell_command(
        f"dvc push {dvc_raw_data_folder}.dvc --remote {dvc_remote_name}"
    )  # push the data to the reomte storage
    run_shell_command("git push --follow-tags")  # push the changes wit the tags
    run_shell_command("git push -f --tags")


def make_new_data_version(dvc_raw_data_folder: str, dvc_remote_name: str) -> None:
    try:
        status = run_shell_command(f"dvc status {dvc_raw_data_folder}.dvc")  # check if the data status change or not
        if (
            status == "Data and pipelines are up to date.\n"
        ):  # we but the status under try statment cuz this command return error is the datafolder.dvc dose not exist cuz the data not version yet
            DATA_UTILS_LOGGER.info("Data and pipelines are up to date.")
            return
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)
    except CalledProcessError:
        commit_to_dvc(dvc_raw_data_folder, dvc_remote_name)
