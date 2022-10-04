import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(f'Error: Usage: {sys.argv[0]} <builder info> <image digest>')

    representation = {
        'image': {
            'digest': sys.argv[2],
        },
        'builder': sys.argv[1],
    }

    print(representation)
