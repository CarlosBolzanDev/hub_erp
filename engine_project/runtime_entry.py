"""Runtime entry point with explicit headless/gui modes."""

from __future__ import annotations

import argparse

from app.core.engine import Engine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generic Python runtime engine")
    parser.add_argument("--mode", choices=["headless", "gui"], default="headless")
    parser.add_argument("--once", action="store_true", help="In headless mode, load selected scripts and exit.")
    return parser.parse_args()


def run() -> None:
    args = parse_args()
    engine = Engine()
    if args.mode == "gui":
        engine.launch_gui()
    else:
        engine.run_headless(run_loop=not args.once)


if __name__ == "__main__":
    run()
