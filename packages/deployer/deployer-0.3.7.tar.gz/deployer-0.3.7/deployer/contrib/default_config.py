from deployer.contrib.nodes.connect import Connect
from deployer.host import LocalHost
from deployer.node import Node, map_roles


class localhost(LocalHost):
    slug = 'localhost'


class example_settings(Node):
    class Hosts:
        host = { localhost }

    class examples(Node):
        def say_hello(self):
            self.hosts.run('echo hello world')

        def directory_listing_in_superuser_home(self):
            self.hosts.sudo('ls ~')

        def return_hello_world(self):
            return 'Hello world'

        def raise_exception(self):
            raise Exception('Custom exception')

    connect = map_roles('host')(Connect.Array)
