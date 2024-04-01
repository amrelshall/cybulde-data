from hydra.core.config_store import ConfigStore
from pydantic.dataclasses import dataclass


@dataclass
class Config:
    dvc_remote_name: str = "gdrive"
    dvc_remote_url: str = "gdrive://1dVLZt8La8m7HKLRRm8OFd9jGnWct3xMl"
    dvc_raw_data_folder: str = "./data/raw"


def setup_config() -> None:
    cs = ConfigStore.instance()
    cs.store(name="config_schema", node=Config)
