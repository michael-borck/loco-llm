"""LocoLLM command-line interface."""

import argparse

from locollm import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="loco",
        description="LocoLLM: Local Collaborative LLMs",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()
    print(f"LocoLLM v{__version__} - not yet implemented")


if __name__ == "__main__":
    main()
