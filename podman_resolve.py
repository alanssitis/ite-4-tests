#!/usr/bin/env python3

import podman


class PodmanEngine:

    def __init__(self):
        try:
            self.client = podman.PodmanClient()
        except Exception as exception:
            raise exception

    def get_image_attrs(self, image_name):
        try:
            image = self.client.images.get(image_name)
        except Exception as exception:
            raise exception
        return image.attrs
