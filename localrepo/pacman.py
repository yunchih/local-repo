# pacman.py
# vim:ts=4:sw=4:noexpandtab

from os import chdir, getuid
from os.path import exists, isdir
from subprocess import call, check_output, CalledProcessError

from localrepo.utils import LocalRepoError

class PacmanError(LocalRepoError):
	''' Handles pacman errors '''
	pass


class PacmanCallError(PacmanError):
	''' Handles call errors '''

	def __init__(self, cmd):
		''' Sets the error message '''
		super().__init__(_('An error occurred while running: {0}').format(cmd))


class Pacman:
	''' A wrapper for program calls of the pacman package '''

	#: Path to su
	SU = '/bin/su'

	#: Path to sudo
	SUDO = '/usr/bin/sudo'

	#: Path to pacman
	PACMAN = '/usr/bin/pacman'

	#: Path to makepkg
	MAKEPKG = '/usr/bin/makepkg'

	#: Path to repo-add
	REPO_ADD = '/usr/bin/repo-add'

	#: Path to repo-remove
	REPO_REMOVE = '/usr/bin/repo-remove'

	#: Path to repo-elephant
	REPO_ELEPHANT = '/usr/bin/repo-elephant'

	@staticmethod
	def call(cmd):
		''' Calls a command '''
		if type(cmd) is str:
			cmd = [cmd]

		if call(cmd) is not 0:
			raise PacmanCallError(' '.join(cmd))

	@staticmethod
	def install(pkgs, as_deps=False):
		''' Installs packages '''
		cmd = [Pacman.PACMAN, '-S'] + pkgs

		if as_deps:
			cmd.append('--asdeps')

		if getuid() is not 0:
			if exists(Pacman.SUDO):
				cmd.insert(0, Pacman.SUDO)
			else:
				cmd = [Pacman.SU, '-c', '\'{0}\''.format(' '.join(cmd))]

		Pacman.call(cmd)

	@staticmethod
	def check_deps(pkgs):
		''' Checks for unresolved dependencies '''
		cmd = [Pacman.PACMAN, '-T'] + pkgs

		try:
			check_output(cmd)
			return []
		except CalledProcessError as e:
			if e.returncode is 127:
				return [p for p in e.output.decode('utf8').split('\n') if p]

			raise PacmanCallError(' '.join(cmd))

	@staticmethod
	def make_package(path, log=False):
		''' Calls makepkg '''
		try:
			chdir(path)
		except:
			raise PacmanError(_('Could not change working directory: {0}').format(path))

		cmd = [Pacman.MAKEPKG, '-d']

		if log:
			cmd += ['-L', '-m']

		Pacman.call(cmd)

	@staticmethod
	def repo_add(db, pkgs):
		''' Calls repo-add  '''
		Pacman.call([Pacman.REPO_ADD, db] + pkgs)

	@staticmethod
	def repo_remove(db, pkgs):
		''' Calls repo-remove '''
		Pacman.call([Pacman.REPO_REMOVE, db] + pkgs)

	@staticmethod
	def repo_elephant():
		''' The elephant never forgets '''
		if call([Pacman.REPO_ELEPHANT]) is not 0:
			raise PacmanError(_('Ooh no! Somebody killed the repo elephant'))
