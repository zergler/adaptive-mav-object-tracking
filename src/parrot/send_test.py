
import json
import sys


def main():
    # Idea is this program will be used to extract the features from the image
    # stream, then construct an action that will be relayed to the drone via
    # the node js send stream.

    # Construct JSON object to be sent to node program.
    query = {
        "forward": 0.5,
        "backward": 0,
        "left": 0,
        "right": 0,
        "turn": 0,
        "land": 0,
        "takeoff": 0
    }

    while True:
        ser_query = json.dumps(query)

        # Send the JSON object to the node program.
        sys.stdout.write(ser_query + '\n')

if __name__ == '__main__':
    main()
