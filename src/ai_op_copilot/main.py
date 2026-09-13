import argparse
import sys


class HelpOnErrorParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(file=sys.stderr)
        self.exit(2, f"\nError: {message}\n")


def main():
    parser = HelpOnErrorParser(description="KyraIO - AI Operations Copilot")
    parser = argparse.ArgumentParser(description="KyraIO - AI Operations Copilot")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="start the CLI instead of the web server",
    )
    args = parser.parse_args()

    if not sys.argv[1:]:
        import uvicorn

        uvicorn.run(
            "ai_op_copilot.api.server:app",
            host="0.0.0.0",
            port=8000,
        )

    elif args.cli:
        from .cli import main as run_cli

        run_cli()
