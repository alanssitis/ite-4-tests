#!/usr/bin/env python3
"""
A test rendition of obtaining a hash from a container being built

Structure of hashable object similar to Red Hat's signing format like cosign
[https://www.redhat.com/en/blog/container-image-signing]

Should be changed to better suit our needs.
Suggestions to the structure:
    * Move creator and timestamp to "critical"
    * Make it so that objects under "critical" don't have to be explicitly
      labelled and be an encoded version if user desires to hide details

{
    "critical": {
        "identity": {
            "docker-reference": [DOCKERFILE-HASH?/MANIFEST]
        },
        "image": {
            "Docker-id": [DOCKER-ID]
        },
        "type": [BUILDER USED]
    },
    "optional": {
        "creator": [USERNAME]
        "timestamp": [TIME BUILT]
    }
}

Worth looking into create a standard interface for resolvers...!?
"""

import os
import sys

import docker
import json
import securesystemslib.formats
import securesystemslib.hash


DEFAULT_HASH_ALGORITHM = 'sha256'
DEFAULT_HASH_LIBRARY = 'hashlib'
SUPPORTED_LIBRARIES = ['hashlib']


def hash_artifacts(client, image, dockerfile, hash_algorithms=None):
    """Create a dictionary of hashes of a container build step

    Parameters:
        client (docker.DockerClient): Class of the docker client
        image (docker.Image): Class of the docker image
        dockerfile (str): Path to dockerfile
        hash_algorithms (list[str]): List of hash algorithms to be used

    Return:
        hash_dict (dict(str:str)): Dictionary containing all hashes of step

    """
    if not hash_algorithms:
        hash_algorithms = ['sha256']

    securesystemslib.formats.HASHALGORITHMS_SCHEMA.check_match(hash_algorithms)
    hash_dict = {}

    for algorithm in hash_algorithms:

        digest_object = securesystemslib.hash.digest(
            algorithm, securesystemslib.hash.DEFAULT_HASH_LIBRARY)

        representation = {
            "critical": {
                "identity": {
                    "docker-reference": {
                        algorithm: securesystemslib.hash.digest_filename(
                            dockerfile, algorithm)
                    },
                },
                "image": {
                    "Docker-id": image.id,
                },
                "type": client.version(),
            },
            "optional": {
                "creator": os.getlogin(),
                "timestamp": "",    # Unsure if this should be used
            },
        }
        str_representation = json.dumps(
            representation, sort_keys=True).encode()

        digest_object.update(str_representation)
        hash_dict.update({algorithm: digest_object.hexdigest()})

    return hash_dict


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(f"Error: Usage: {sys.argv[0]} <path> <tag> <dockerfile>")

    client = docker.from_env()
    image, _ = client.images.build(
        path=sys.argv[1], tag=sys.argv[2], dockerfile=sys.argv[3])
    generated_hash = hash_artifacts(client, image, sys.argv[3])
    print(generated_hash)
