##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## main
##

import argparse
from zappy import logger
from zappy.ai import ZappyAI
from zappy.exception import ZappyError

ZAPPY_AI_ERROR = 84
ZAPPY_AI_SUCCESS = 0

def main():
    """
    Entry point of the Zappy AI client.
    """
    parser = argparse.ArgumentParser(description="Zappy AI Client", add_help=False)
    parser.add_argument('-p', '--port', type=int, required=True, help='Port to connect to the Zappy server')
    parser.add_argument('-n', '--name', type=str, required=True, help='Name of the team to join')
    parser.add_argument('-h', '--host', type=str, default='localhost', help='Host to connect to the Zappy server')

    args = parser.parse_args()

    success = False
    try:
        ai_client = ZappyAI(host=args.host, port=args.port, team_name=args.name)
        success = ai_client.run()
    except ZappyError as e:
        logger.error(f"An error occurred at: {e.where}: {e.what}")
        success = False
    exit(ZAPPY_AI_SUCCESS if success else ZAPPY_AI_ERROR)

if __name__ == "__main__":
    main()
