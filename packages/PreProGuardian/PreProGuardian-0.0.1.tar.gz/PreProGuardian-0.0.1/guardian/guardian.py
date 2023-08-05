import subprocess
from Queue import Queue, Empty
from threading import Thread
import sys, os, json, itertools, time

class Guardian(object):
	class GuardianError(Exception):
		pass

	class Watcher(object):
		ptype        = ''
		folders      = []
		sources_root = ''
		static_root  = ''
		def __init__(self, config, sources_root, static_root):
			self.sources_root = sources_root
			self.static_root  = static_root
			if not self.ptype:
				raise Guardian.GuardianError("Watcher %s has it's type not defined" % self.__class__.__name__)
			try:
				self.folders = config[self.ptype]
			except KeyError:
				self.folders = []
		def commands(self):
			pass
	class SassWatcher(Watcher):
		ptype     = 'sass'
		def commands(self):
			if len(self.folders):
				return [
					"sass --watch %s" %
				    " ".join(["%s:%s" % (
				        os.path.join(self.sources_root, f),
				        os.path.join(self.static_root,  f)
				    ) for f in self.folders])
				]
			return []
	class JadeWatcher(Watcher):
		ptype     = 'jade'
		def commands(self):
			return [
				"jade --watch --out %s %s"  % (
					os.path.join(self.static_root,  f),
			        os.path.join(self.sources_root, f)
				)
				for f in self.folders
			]
	class CoffeeWatcher(Watcher):
		ptype     = 'coffee'
		def commands(self):
			return [
				"coffee --watch --map -o %s %s" % (
					os.path.join(self.static_root,  f),
				    os.path.join(self.sources_root, f)
				)
			    for f in self.folders
			]

	config       = False
	sources_root = False
	static_root  = False
	def __init__(self, config_file=""):
		try:
			self.config       = json.load(open(config_file))
		except ValueError as e:
			raise Guardian.GuardianError("Config file is corrupted: %s" % str(e))
		try:
			self.sources_root = (self.config['sources_root']+"/").replace("//", "/")
			self.static_root  = (self.config['static_root']+"/").replace("//", "/")
		except KeyError:
			raise Guardian.GuardianError("Config must contain following fields:\n\nsources_root - for where to look for sources\nstatic_root  - for where to put results")
		if not os.path.exists(self.sources_root):
			raise Guardian.GuardianError("Sources root dir does not exist")
		if not os.path.exists(self.static_root):
			raise Guardian.GuardianError("Destination folder does not exist")
		if 'consistency_check' in self.config:
			self.check_consistency()
		self.run()
	def check_consistency(self):
		print "Checking consistency..."
		folders  = [root.replace(self.config['sources_root'], "") for root, dirs, files in os.walk(self.sources_root, followlinks=True) if root.replace(self.config['sources_root'], "")]
		tocreate = []
		for f in folders:
			if not os.path.exists(os.path.join(self.static_root, f)):
				tocreate.append(f)
		if len(tocreate):
			print "Following directories don't exist in destination folder:\n\n"
			print "\n".join(tocreate)
			print "\nCreate them? (Y/n)"
			answer = raw_input()
			if answer.strip().lower() == 'y':
				for f in tocreate:
					try:
						os.mkdir(os.path.join(self.static_root, f))
					except OSError as e:
						raise Guardian.GuardianError("Unable to create folder: %s" % (str(e)))
			else:
				raise Guardian.GuardianError("consistency_check was set to True in configuration file.\nEither disable it or create subfolders in destination folder")

	def run(self):
		print "Running..."
		watchers = Guardian.Watcher.__subclasses__()
		commands = [c.split(" ") for c in list(itertools.chain.from_iterable([c(self.config, self.sources_root, self.static_root).commands() for c in watchers]))]
		q = Queue()
		threads = []
		if not len(commands):
			raise Guardian.GuardianError("No watchers defined in config file")
		print "\n".join([" ".join(c) for c in commands])

		def enqueue_output(out, err, queue):
			for _line in iter(out.readline, b''):
				queue.put((1, _line))
			for _line in iter(err.readline, b''):
				queue.put((2, _line))
			out.close()
		def start_thread(_command):
			p = subprocess.Popen(args=_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			thread = Thread(target=enqueue_output, args=(p.stdout, p.stderr, q))
			thread.daemon = True
			thread.start()
			return thread
		def err_print(text):
			print '\033[91m'+text+'\033[0m'
		for command in commands:
			threads.append([start_thread(command), command])
		while True:
			try:
				line = q.get_nowait()
				if line[0] == 1:
					line = line[1].strip()
					if line.split(" ")[0].lower() == 'error':
						err_print(line)
					else:
						print line
				else:
					err_print(line[1].strip())
			except Empty:
				for t in threads:
					if not t[0].isAlive():
						err_print('\n\nThread died! Press enter to restart automatically...\n\n')
						a = raw_input().strip()
						if not a:
							t[0] = start_thread(t[1])
						else:
							sys.exit()

				time.sleep(.3)


if __name__ == '__main__':
	g = Guardian('test-config.json')
