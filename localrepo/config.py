# config.py
# vim:ts=4:sw=4:noexpandtab

from os import makedirs
from os.path import abspath, dirname, exists, expanduser, isdir, join
from configparser import ConfigParser

class ConfigError(Exception):
	''' The config error class '''

	def __init__(self, msg):
		''' Sets the error message '''
		self._msg = msg

	def message(self):
		''' Returns the error message '''
		return self._msg

	def __str__(self):
		''' Returns the error message '''
		return self._msg


class Config:
	''' A wrapper for the ConfigParser class '''

	#: Path to the config file
	CONFIGFILE = expanduser(join('~', '.config', 'local-repo'))

	#: The ConfigParser instance
	_parser = ConfigParser()

	#: The used repo
	_repo = None

	@staticmethod
	def init(repo, path=CONFIGFILE):
		''' Sets the repo and loads the config file '''
		Config._repo = repo
		path = abspath(path)

		if not exists(path):
			return

		try:
			Config._parser.readfp(open(path))
		except:
			raise ConfigError(_('Could not parse config file: {0}').format(path))

		if not Config._parser.has_section(repo):
			Config._repo = Config.find_repo_by_path(repo)

	@staticmethod
	def normalize_path(path):
		''' Normalizes a repo path to make it compareable.
		E.g. /path/to/repo equals /path/to/repo/mydb.db.tar.gz '''
		path = abspath(path)
		return path if exists(path) and isdir(path) else dirname(path)

	@staticmethod
	def find_repo_by_path(path):
		''' Finds the repo name by path '''
		path = Config.normalize_path(path)

		for repo in (s for s in Config._parser.sections() if Config._parser.has_option(s, 'path')):
			if Config.normalize_path(Config._parser.get(repo, 'path')) == path:
				return repo

		return path

	@staticmethod
	def get(option, default=None):
		''' Returns an option '''
		try:
			return Config._parser.get(Config._repo, option)
		except:
			return default

	@staticmethod
	def get_all():
		''' Returns all available options '''
		try:
			return dict(Config._parser.items(Config._repo))
		except:
			return {}

	@staticmethod
	def set(option, val):
		''' Sets an option '''
		if not Config._parser.has_section(Config._repo):
			Config._parser.add_section(Config._repo)

		Config._parser.set(Config._repo, option, val)

	@staticmethod
	def remove_repo():
		''' Removes the repo from the config '''
		Config._parser.remove_section(Config._repo)

	@staticmethod
	def save(path=CONFIGFILE):
		''' Saves options to config file '''
		try:
			makedirs(dirname(path), mode=0o755, exist_ok=True)
			Config._parser.write(open(path, 'w'))
		except:
			raise ConfigError(_('Could not save config file: {0}').format(path))
