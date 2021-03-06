#!/usr/bin/env python3

import docker


class DockerEngine:

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as exception:
            raise exception

    def get_image_attrs(self, image_name):
        try:
            image = self.client.images.get(image_name)
        except Exception as exception:
            raise exception
        return image.attrs
