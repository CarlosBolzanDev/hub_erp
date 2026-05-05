from __future__ import annotations

import argparse
import json
import sys

from runtime_bridge import RuntimeBridge


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embedded Python script launcher")
    parser.add_argument("--script", required=True, help="Path to the .py script to execute")
    parser.add_argument("--context", required=True, help="Path to the JSON context file")
    parser.add_argument("--log", required=True, help="Path to the execution log file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bridge = RuntimeBridge(args.script, args.context, args.log)
    result = bridge.run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
