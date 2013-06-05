from ConfigParser import SafeConfigParser
from optparse import OptionParser
import logging
import os

CONFIG_FILENAMES = ['/etc/fts3/fts3client.cfg',
										os.path.expanduser('~/.fts3client.cfg')]

CONFIG_DEFAULTSECTION = 'Main'
CONFIG_DEFAULTS = {
										'verbose': 'false',
										'endpoint': None,
										'json': 'false',
										'ukey': None,
										'ucert': None
									}

class Base(object):
	
	def __init__(self, extra_args = None):
		self.logger = logging.getLogger()
		
		# Common CLI options
		usage = None
		if extra_args:
			usage = "usage: %prog [options] " + extra_args

		config = SafeConfigParser(defaults=CONFIG_DEFAULTS)

		section = CONFIG_DEFAULTSECTION
		config.read(CONFIG_FILENAMES)

		# manually set the section in edge cases
		if not config.has_section('Main'):
			section = 'DEFAULT'
		
		self.optParser = OptionParser(usage = usage)
		
		self.optParser.add_option('-v', '--verbose', dest = 'verbose', action = 'store_true',
								  help = 'verbose output.', default=config.getboolean(section, 'verbose'))
		self.optParser.add_option('-s', '--endpoint', dest = 'endpoint',
								  help = 'FTS3 REST endpoint.', default=config.get(section, 'endpoint'))
		self.optParser.add_option('-j', dest = 'json', action = 'store_true',
								  help = 'print the output in JSON format.',
									default=config.get(section, 'json'))
		self.optParser.add_option('--key', dest = 'ukey',
								  help = 'the user certificate private key.',
									default=config.get(section, 'ukey'))
		self.optParser.add_option('--cert', dest = 'ucert',
								  help = 'the user certificate.',
									default=config.get(section, 'ucert'))
