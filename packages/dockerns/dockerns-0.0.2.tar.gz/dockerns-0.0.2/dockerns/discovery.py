import re
import time
import docker
import logging


class Discovery:
    """
    Docker Container Discovery
    """

    root = ".docker.local"

    aliases = {}
    services = {}
    services_cache = 0

    def __init__(self, host, version="1.8", root=".docker.local", aliases={}):
        """
        Construct

        @param   {string}  host     Docker Host
        @param   {string}  version  Docker API Version
        @return  {void}
        """

        self.docker = docker.Client(base_url=host, version=version,
                                    timeout=10)

        self.root = root
        self.aliases = aliases

    def inspect(self):
        """
        Inspect Running Containers

        @method  inspect
        @return  {list}
        """

        inspected = []

        # List Running Containers
        containers = self.docker.containers(quiet=False, all=False,
                                            trunc=False, latest=False,
                                            since=None, before=None,
                                            limit=-1)

        # Inspect Containers
        for container in containers:
            inspected.append(self.docker.inspect_container(container['Id']))

        return inspected

    def update_aliases(self):
        """
        Update Aliases

        @method  update_aliases
        @return  {dict}
        """

        for alias, host in self.aliases.iteritems():
            ip = self.services.get(host, False)

            if ip is not False:
                self.services[alias] = ip

        return self.services

    def get_services(self):
        """
        Get DNS Services

        @method  get_services
        @return  {dict}
        """

        # Use Cache
        if (time.time() - self.services_cache) < 30:
            logging.debug("Using cached services")
            logging.debug(self.services)
            return self.services

        # Inspect All Containers
        logging.debug("Fetching fresh services")
        containers = self.inspect()

        # Scrape Services
        for container in containers:
            address = container['NetworkSettings']['IPAddress']

            # Build Custom Name
            name = container['Name'].replace('_', '-').lower()
            name = re.sub(r'[^a-z0-9\-\.]+', '', name)

            # Add Versions to Services
            self.services[name + self.root] = address
            self.services[container['ID'] + self.root] = address
            self.services[container['Config']['Hostname']+self.root] = address

        # Update Aliases
        self.update_aliases()

        self.services_cache = time.time()
        logging.debug(self.services)

        return self.services
