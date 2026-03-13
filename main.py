"""AtomSculptor – CLI entry-point.

Usage:
    python main.py                  # interactive ADK CLI (default)
    python main.py --web            # launch the 4-panel web GUI
    python main.py --web --port 9000
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="AtomSculptor agent team")
    parser.add_argument("--web", action="store_true", help="Launch the web GUI")
    parser.add_argument("--host", default="0.0.0.0", help="Web server bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Web server port (default: 8000)")
    args = parser.parse_args()

    if args.web:
        from web_gui.server import run_server
        run_server(host=args.host, port=args.port)
    else:
        # Fall through to Google ADK CLI
        try:
            from google.adk.cli import main as adk_main
            sys.argv = [sys.argv[0]]  # strip our flags so ADK CLI doesn't choke
            adk_main()
        except ImportError:
            print("google-adk CLI not available. Use --web for the web GUI.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
