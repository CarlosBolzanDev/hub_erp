"""Generic runtime entry point for the Python script engine."""

from app.core.engine import Engine


def run() -> None:
    engine = Engine()
    engine.start()


if __name__ == "__main__":
    run()
