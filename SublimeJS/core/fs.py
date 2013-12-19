import threading
import sublime
import codecs
import threading
import os

from PyV8 import JSObject, JSArray, JSFunction
from SublimeJS.v8 import getContext, convert

class FileSystem:
	def __args(self, path, options, callback=None):
		if(type(options) == JSFunction or options == None):
			callback = options
			options = { 'flag':'r', 'encoding':'utf-8' }
		if(type(options) == JSObject):
			options = convert(options)

		flag = 'r'
		encoding = 'utf-8'

		if('flag' in options):
			flag = options['flag']
		if('encoding' in options):
			encoding = options['encoding']
		
		return (path, flag, encoding, callback)

	def readFile(self, path, options=None, callback=None):
		
		def _call(path, flag, encoding, callback, *args):
			err = None
			content = None
			try:
				f = codecs.open(path, flag, encoding);
				content = f.read()
				f.close()
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err, content)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)

		thread = threading.Thread(target=_call, args=self.__args(path, options, callback))
		thread.start()


	def readFileSync(self, path, options=None):
		(path, flag, encoding, _) = self.__args(path, options)	
		return codecs.open(path, flag, encoding).read();

	def writeFile(self, path, data, options=None, callback=None):

		def _call(path, flag, encoding, callback, data, *args):
			err = None
			try:
				f = codecs.open(path, flag, encoding);
				f.write(data)
				f.close()
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)

		thread = threading.Thread(target=_call, args=self.__args(path, options, callback)+(data,))
		thread.start()

	def writeFileSync(self, path, data, options=None):
		(path, flag, encoding, _) = self.__args(path, options)	
		return codecs.open(path, flag, encoding).write(data);

	def chmod(self, path, mode, callback=None):
		def _call(path, mode, callback, *args):
			err = None
			try:
				os.chmod(path, mode)
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, mode, callback))
		thread.start()		

	def chmodSync(self, path, mode):
		return os.chmod(path, mode)

	def mkdir(self, path, callback):
		def _call(path, callback, *args):
			err = None
			try:
				os.mkdir(path)
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, callback))
		thread.start()

	def mkdirSync(self, path):
		return os.mkdir(path)

	def rmdir(self, path, callback):
		def _call(path, callback, *args):
			err = None
			try:
				os.rmdir(path)
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, callback))
		thread.start()

	def rmdirSync(self, path):
		return os.rmdir(self)

	def readdir(self, path, callback):
		def _call(path, callback, *args):
			err = None
			files = JSArray([])
			try:
				files = JSArray(os.listdir(path))
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err, files)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, callback))
		thread.start()

	def readdirSync(self, path):
		return JSArray(os.listdir(path))

	def exists(self, path, callback):
		def _call(path, callback, *args):
			err = None
			r = False
			try:
				r = os.path.exists(path)
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(r)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, callback))
		thread.start()	

	def existsSync(self, path):
		return os.path.exists(path)	

	def stat(self, path, callback):
		def _call(path, callback, *args):
			err = None
			stats = None
			try:
				stats = self.statSync(path)
			except Exception as e:
				err = e
			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(err, stats)
					ctx._js_ctx.leave()
				sublime.set_timeout(_callback, 0)
		thread = threading.Thread(target=_call, args=(path, callback))
		thread.start()

	def statSync(self, path):
		stat = os.stat(path)
		r = { }
		i = 0
		for k in ['st_mode', 'st_ino', 'st_dev', 'st_nlink', 'st_uid', 'st_gid', 'st_size', 'st_atime', 'st_mtime', 'st_ctime']:
			r[k] = stat[i]
			i = i + 1
		r['isFile'] = lambda: os.path.isfile(path)
		r['isDirectory'] = lambda: os.path.isdir(path)
		r['isSymbolicLink'] = lambda: os.path.islink(path)
		return r

	# def fstat():
	#	pass

	# def lstat():
	#	pass

def exports():
	return FileSystem()
