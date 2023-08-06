#!/usr/bin/env python

import argparse
import collections
import json
import logging
import os
import sys

from . import __title__
from . import __version__
from .remote import Remote

def read_config():
	config = collections.defaultdict(lambda: None, {
		"name": "samsungctl",
		"description": "PC",
		"id": "",
		"port": 55000,
	})

	config_directory = os.getenv("XDG_CONFIG_HOME") or os.path.join(os.getenv("HOME"), ".config")

	try:
		config_file = open(os.path.join(config_directory, "samsungctl.conf"))
	except FileNotFoundError:
		return config

	with config_file:
		try:
			config_json = json.load(config_file)
		except ValueError as e:
			logging.warning("Warning: Could not parse the configuration file.\n  %s", e)
			return config

		config.update(config_json)

	return config

def main():
	parser = argparse.ArgumentParser(prog=__title__,
	                                 description="Remote control Samsung televisions via TCP/IP connection.",
	                                 epilog="E.g. %(prog)s --host 192.168.0.10 --name myremote KEY_VOLDOWN")
	parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
	parser.add_argument("-v", action="count", help="increase output verbosity")
	parser.add_argument("-q", action="store_true", help="suppress non-fatal output")
	parser.add_argument("key", nargs="+", help="keys to be sent (e.g. KEY_VOLDOWN)")
	parser.add_argument("--host", help="TV hostname or IP address")
	parser.add_argument("--name", help="remote control name")
	parser.add_argument("--description", help="remote control description")
	parser.add_argument("--id", help="remote control id")
	parser.add_argument("--port", type=int, help="TV port number (TCP)")

	args = parser.parse_args()

	if args.q:
		log_level = logging.ERROR
	elif not args.v:
		log_level = logging.WARNING
	elif args.v == 1:
		log_level = logging.INFO
	else:
		log_level = logging.DEBUG

	logging.basicConfig(format="%(message)s", level=log_level)

	config = read_config()

	host = args.host or config["host"]
	name = args.name or config["name"]
	description = args.description or config["description"]
	id = args.id or config["id"]
	port = args.port or config["port"]

	if not host:
		logging.error("Error: --host must be set")
		return

	try:
		remote = Remote(host, port, name, description, id)
	except Remote.AccessDenied:
		logging.error("Error: Access denied!")
		return

	with remote:
		for key in args.key:
			remote.control(key)

main()
