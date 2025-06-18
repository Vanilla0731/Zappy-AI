##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## main
##

import sys
import argparse
from zappy.ai import ZappyAI

def main():
    """
    Entry point of the Zappy AI client.
    """
    parser = argparse.ArgumentParser(description="Zappy AI Client", add_help=False)
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to connect to the Zappy server')
    parser.add_argument('-n', '--name', type=str, required=True, help='Name of the team to join')
    parser.add_argument('-h', '--host', type=str, default='localhost', help='Host to connect to the Zappy server')

    args = parser.parse_args()

    try:
        ai_client = ZappyAI(host=args.host, port=args.port, team_name=args.name)
        ai_client.run()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"A critical error occurred: {e}", file=sys.stderr)
        sys.exit(84)

if __name__ == "__main__":
    main()
