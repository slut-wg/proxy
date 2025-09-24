from .utils import *
from .models.config import Config
import trio
from hypercorn.config import Config as HyperConfig
from hypercorn.trio import serve # pyright: ignore[reportUnknownVariableType]

def main(hypercorn_config: HyperConfig, slut_config: Config):
    from .app import build_app

    app = build_app(slut_config)

    _ = trio.run(serve, app, hypercorn_config) # pyright: ignore[reportArgumentType]

# FIXME: real cli
def cli_entrypoint():
    hyper = HyperConfig()
    hyper.bind = ["localhost:8080"]

    conf = Config.from_toml("config.toml")

    main(hyper, conf)

if __name__ == "__main__":
    cli_entrypoint()