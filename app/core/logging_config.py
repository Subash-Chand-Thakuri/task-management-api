import logging


def configure_app_logging(level: int = logging.INFO) -> None:
    """Ensure app.* loggers print to the console when running under uvicorn."""
    app_logger = logging.getLogger("app")
    app_logger.setLevel(level)

    if not app_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(levelname)s: %(name)s - %(message)s")
        )
        app_logger.addHandler(handler)

    app_logger.propagate = False
