"""
A test rendition of obtaining a hash from a container being built

Structure of hashable object similar to Red Hat's signing format used in cosign
[https://www.redhat.com/en/blog/container-image-signing]

Should be changed to better suit our needs.

{
    'image': {
        'attrs': [IMAGE ATTRIBUTE HASH]
    },
    'builder': [BUILDER USED]
}

Worth looking into create a standard interface for resolvers...!?
(i.e., Create a format of a class that can just be imported and pluged-in!)

Code is inspired by the source of securesystemslib.hash and in-toto
"""
import json
import re
import sys

from docker_resolve import DockerEngine
from podman_resolve import PodmanEngine
import securesystemslib.formats
import securesystemslib.hash

CONTAINER_ENGINES = {
    "docker": DockerEngine,
    "podman": PodmanEngine,
}


def _hash_image_attrs(attrs,
                      algorithm=securesystemslib.hash.DEFAULT_HASH_ALGORITHM,
                      hash_library=securesystemslib.hash.DEFAULT_HASH_LIBRARY):
    """Hash container image attrs with desired hashing algorithm

    Parameters:
        attrs (dict): Docker container image attrs object
        algorithm (str): The hash algorithm
        hash_library (str): The library providing the hash

    Return:
        (str): Hash of the attrs dictionary of a container image
    """
    securesystemslib.formats.NAME_SCHEMA.check_match(algorithm)
    securesystemslib.formats.NAME_SCHEMA.check_match(hash_library)

    digest_object = securesystemslib.hash.digest(algorithm, hash_library)
    if 'Metadata' in attrs:
        attrs.pop('Metadata')
    digest_object.update(json.dumps(attrs, sort_keys=True).encode())

    return digest_object.hexdigest()


def digest_image(image_name, builder, hash_algorithms):
    """Create a dictionary of hashes of a container image

    Parameters:
        image_name (str): Name of image
        builder (str): Name of container client used
        hash_algorithms (list[str]): List of hash algorithms to be used

    Return:
        hash_dict (dict{str:str}): Dictionary containing all hashes of step
    """
    if builder not in CONTAINER_ENGINES:
        sys.exit(f"{builder} not supported")

    try:
        engine = CONTAINER_ENGINES[builder]()
        attrs = engine.get_image_attrs(image_name)
    except Exception as exception:
        sys.exit(exception)

    if not hash_algorithms:
        hash_algorithms = ['sha256']

    securesystemslib.formats.HASHALGORITHMS_SCHEMA.check_match(hash_algorithms)
    hash_dict = {}

    for algorithm in hash_algorithms:
        digest_object = securesystemslib.hash.digest(
            algorithm, securesystemslib.hash.DEFAULT_HASH_LIBRARY)

        representation = {
            'image': {
                'attrs': _hash_image_attrs(attrs, algorithm),
            },
            'builder': engine.client.version(),
        }

        digest_object.update(
            json.dumps(representation, sort_keys=True).encode())
        hash_dict.update({algorithm: digest_object.hexdigest()})

    return hash_dict


if __name__ == '__main__':
    if len(sys.argv) != 2 or not re.match(r'(docker|podman):.+', sys.argv[1]):
        sys.exit(f'Error: Usage: {sys.argv[0]} <builder>:<image-name>')

    builder, image = sys.argv[1].split(":", 1)

    hash_algorithms = ['sha256', 'sha512', 'md5']
    generated_hash = digest_image(image, builder, hash_algorithms)
    # json.dumps to make print more legible
    print(json.dumps(generated_hash, indent=4))
