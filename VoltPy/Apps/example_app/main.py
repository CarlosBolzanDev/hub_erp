import voltpy.pandas as pd
from voltpy import system


def main() -> None:
    frame = pd.DataFrame(
        [
            {"product": "VoltPy Core", "version": "0.1"},
            {"product": "VoltPy Loader", "version": "0.1"},
        ]
    )
    print(f"App {system.app_name()} running from {system.app_dir()}")
    print(frame.to_string(index=False))


if __name__ == "__main__":
    main()
