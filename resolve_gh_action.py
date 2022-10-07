import json
import sys

import securesystemslib.formats
import securesystemslib.hash


def digest_container_build_push(standard, tag, digest, hash_algorithms):
    if not hash_algorithms:
        hash_algorithms = ['sha256']

    securesystemslib.formats.HASHALGORITHMS_SCHEMA.check_match(hash_algorithms)
    hash_dict = {}

    digest_alg, digest_val = digest.split(':')

    for algorithm in hash_algorithms:
        digest_object = securesystemslib.hash.digest(
            algorithm, securesystemslib.hash.DEFAULT_HASH_LIBRARY)

        representation = {
            f'{standard}://{tag}': {
                digest_alg: digest_val,
            },
        }

        digest_object.update(
            json.dumps(representation, sort_keys=True).encode())
        hash_dict.update({algorithm: digest_object.hexdigest()})

    return hash_dict


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(f'Error: Usage: {sys.argv[0]} <standard> <tag> <digest>')

    hash_algorithms = ['sha256', 'sha512', 'md5']

    _ = digest_container_build_push(sys.argv[1], sys.argv[2], sys.argv[3],
                                    hash_algorithms)
    print(_)
