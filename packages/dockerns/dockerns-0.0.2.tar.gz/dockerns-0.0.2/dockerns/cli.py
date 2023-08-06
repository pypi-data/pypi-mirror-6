import sys
import yaml
import logging
import argparse
import discovery
import dnsserver

log_format = "[%(asctime)s] %(levelname)s: %(message)s"


def parse_cli():
    """
    Parse CLI Option

    @method  parse_cli
    @return  {dict}
    """

    parser = argparse.ArgumentParser(description="Docker Service DNS Server")

    parser.add_argument('--debug', action="store_true",
                        default=False, help="Enable Debug Logging")
    parser.add_argument('--config', action="store",
                        default="config.yml", help="Config File")

    return parser.parse_args()


def read_config(filename):
    """
    Read YAML Config File

    @method  read_config
    @param   {string}  filename  Config Filename
    @return  {dict}
    """

    try:
        with open(filename, 'rb') as f:
            config = yaml.load(f)
    except IOError:
        logging.critical("Could not open config file (%s)" % filename)
        sys.exit(1)

    return config


def run():
    """
    Run CLI

    @method  run
    @return  {void}
    """

    # Parse CLI Options
    options = parse_cli()

    # Debug Logging
    if options.debug:
        logging.basicConfig(level=logging.DEBUG, format=log_format)
        logging.debug("Debug logging enabled")
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)

    # Read Config File
    config = read_config(options.config)

    # Create Docker Discovery
    docker = discovery.Discovery(
        host=config.get("docker", "http://127.0.0.1:4243"),
        root=config.get("root", ".docker.local"),
        aliases=config.get("aliases", {}))

    # Create DNS Server
    server = dnsserver.DNSServer(
        host=config.get("host", "127.0.0.1"),
        port=config.get("port", 53))

    server.before_request = docker.get_services

    logging.info("Starting server on port %i..." % config.get("port", 53))

    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        logging.debug('Exiting...')
        sys.exit(0)


# Run Application
if __name__ == "__main__":
    run()
