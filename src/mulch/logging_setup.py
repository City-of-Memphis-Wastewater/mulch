import shutil
import json
import logging.config
from pathlib import Path
from importlib.resources import files, as_file

DEFAULT_LOGGING_JSON = '''
{
  "version": 1,
  "disable_existing_loggers": false,

  "formatters": {
    "default": {
      "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
      "datefmt": "%Y-%m-%d %H:%M:%S"
    }
  },

  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "default",
      "stream": "ext://sys.stdout"
    },
    "file": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "DEBUG",
      "formatter": "default",
      "filename": ".mulch/logs/default.log",
      "maxBytes": 10485760,
      "backupCount": 3,
      "encoding": "utf8"
    }
  },

  "root": {
    "handlers": ["console", "file"],
    "level": "DEBUG"
  }
}
''' 


def ensure_logs_folder_with_config(project_root: Path):
    logs_dir = project_root / ".mulch" / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)

        logging.debug(f"Created logs directory: {logs_dir}")
        logging.info(f"Created logs directory")

    logging_config_path = logs_dir / "logging.json"
    if not logging_config_path.exists():
        try:
            package_files = files("mulch")  

            logging.debug(f"Package files root: {package_files}")
            with as_file(package_files / "logging.json") as src_file:
                shutil.copy(src_file, logging_config_path)
            logging.debug(f"Copied default logging.json to {logging_config_path}")
        except Exception as e:
            logging.debug(f"Failed to copy logging.json: {e}")
            logging_config_path.write_text(DEFAULT_LOGGING_JSON)
    else:
        logging.debug(f"logging_config_path = {logging_config_path}")


def setup_logging_portable():
    config = json.loads(DEFAULT_LOGGING_JSON)
    log_path = Path(".mulch/logs/default.log")
    if not log_path.parent.exists():
        config["handlers"].pop("file", None)
        if "file" in config["root"]["handlers"]:
            config["root"]["handlers"].remove("file")
    logging.config.dictConfig(config)


def setup_logging(project_root: Path | None = None, portable: bool = False):
    if portable:
        return setup_logging_portable()
    else:
        setup_logging_portable() # prepare for initial logging statements and continue
        pass

    if project_root is None:
        project_root = Path.cwd()  
    
    ensure_logs_folder_with_config(project_root)
    config_path = project_root / ".mulch" / "logs" / "logging.json"
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    except Exception as e:

        logging.debug(f"⚠️ Failed to load logging config from {config_path}: {e}")
        logging.info("🔁 Falling back to portable default logging setup.")
        setup_logging_portable()

# Dynamically set logging level, per handler, like when using a GUI
def set_handler_level(handler_name: str, level_name: str):
    logger = logging.getLogger()  # root logger
    level = getattr(logging, level_name.upper(), None)
    if level is None:
        raise ValueError(f"Invalid log level: {level_name}")
    
    for handler in logger.handlers:
        if handler.get_name() == handler_name:
            handler.setLevel(level)
            logging.info(f"Set {handler_name} handler level to {level_name}")
            break
    else:
        raise ValueError(f"Handler '{handler_name}' not found")