import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(f'Error: Usage: {sys.argv[0]} <last git commit> <image digest>')

    representation = {
        'image': {
            'digest': sys.argv[2],
        },
        'context': {
            'commit': sys.argv[1],
            },
        'builder': sys.argv[1],
    }

    print(representation)
