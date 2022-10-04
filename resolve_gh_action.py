import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(f'Error: Usage: {sys.argv[0]} <image id> <image digest>')

    representation = {
        'image': {
            'id': sys.argv[1],
            'digest': sys.argv[2],
        },
        'builder': 'testing'
    }

    print(representation)
