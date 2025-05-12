from mmisp.api.config import Runner, config


def main() -> None:
    if config.RUNNER == Runner.GUNICORN:
        from gunicorn.app.base import BaseApplication  # type: ignore

        from mmisp.api.main import app

        class StandaloneApplication(BaseApplication):
            def __init__(self, app, options=None):  # noqa
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):  # noqa
                assert self.cfg is not None
                config = {
                    key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None
                }
                for key, value in config.items():
                    self.cfg.set(key, value)

            def load(self):  # noqa
                return self.application

        options = {
            "bind": f"{config.BIND_HOST}:{config.PORT}",
            "workers": config.WORKER_COUNT,
            "worker_class": "uvicorn.workers.UvicornWorker",
        }

        StandaloneApplication(app, options).run()
    elif config.RUNNER == Runner.GRANIAN:
        from granian import Granian  # type: ignore

        Granian(
            "mmisp.api.main:app",
            interface="asgi",  # type:ignore
            workers=config.WORKER_COUNT,
            address=config.BIND_HOST,
            port=config.PORT,
        ).serve()  # type:ignore


if __name__ == "__main__":
    main()
