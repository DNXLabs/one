import dockerpty
import docker.utils
import time
from one.docker.client import client
from one.docker.image import Image
import os


image = Image()

class Container:

    def __init__(self):
        pass


    def create(self, image='', command=None, entrypoint=None, stdin_open=True, tty=True, environment=''):
        image.check_image(image)

        container = client.create_container(image,
                                            command=command,
                                            entrypoint=entrypoint,
                                            stdin_open=stdin_open,
                                            tty=tty,
                                            environment=environment,
                                            working_dir='/work',
                                            volumes=['/work'],
                                            host_config=client.create_host_config(
                                                binds={ os.getcwd(): {
                                                    'bind': '/work',
                                                    'mode': 'rw',
                                                    }
                                                }
                                            ))

        if tty:
            dockerpty.start(client, container)
        else:
            client.start(container=container.get('Id'))
            client.wait(container=container.get('Id'))

        logs = client.logs(container['Id'])
        client.remove_container(container)

        return logs