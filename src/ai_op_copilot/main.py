import argparse
import sys


class HelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(file=sys.stderr)
        self.exit(2, f"\nError: {message}\n")


def main():
    parser = HelpOnErrorParser(description="KyraIO - AI Operations Copilot")
    parser = argparse.ArgumentParser(description="KyraIO - AI Operations Copilot")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--cli",
        action="store_true",
        help="start the CLI instead of the web server",
    )
    modes.add_argument(
        "--dev",
        action="store_true",
        help="start the web server with auto-reload and debug logging",
    )
    args = parser.parse_args()

    match args:
        case args.cli:
            from .cli import main as run_cli

            run_cli()

        case _:
            import uvicorn

            uvicorn.run(
                "ai_op_copilot.api.server:app",
                host="0.0.0.0" if args.dev else "127.0.0.1",
                port=8000,
                reload=args.dev,
                log_level="debug" if args.dev else "info",
            )
