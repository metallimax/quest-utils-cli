from importlib import resources as impresources


from dynaconf import Dynaconf


settings_root_path = impresources.files("quest_utils_cli.config")
settings = Dynaconf(settings_file=settings_root_path / "settings.toml")
