# coding=utf-8
import sys
import os
import os.path
import codecs
import json
import gc
import imp
import re

BASE_PATH = os.path.abspath(os.path.dirname(__file__))

is_python3 = sys.version_info[0] > 2

ctx_info = {
	'context': None,
	'callbacks': [],
	'reload_callbacks': []
}

################################################

def should_use_unicode():
	"""
	WinXP unable to eval JS in unicode object (while other OSes requires it)
	This function checks if we have to use unicode when reading files
	"""
	ctx = PyV8.JSContext()
	ctx.enter()
	use_unicode = True
	try:
		ctx.eval(u'(function(){return;})()')
	except:
		use_unicode = False

	ctx.leave()

	return use_unicode

def js_file_reader(file_path, use_unicode=True):

	if hasattr(sublime, 'load_resource'):
		rel_path = file_path
		for prefix in [sublime.packages_path(), sublime.installed_packages_path()]:
			if rel_path.startswith(prefix):
				rel_path = os.path.join('Packages', rel_path[len(prefix) + 1:])
				break

		rel_path = rel_path.replace('.sublime-package', '')
		# for Windows we have to replace slashes
		rel_path = rel_path.replace('\\', '/')
		return sublime.load_resource(rel_path)
		
	if use_unicode:
		f = codecs.open(file_path, 'r', 'utf-8')
	else:
		f = open(file_path, 'r')

	content = f.read()
	f.close()

	return content

def import_pyv8():
	# Importing non-existing modules is a bit tricky in Python:
	# if we simply call `import PyV8` and module doesn't exists,
	# Python will cache this failed import and will always
	# throw exception even if this module appear in PYTHONPATH.
	# To prevent this, we have to manually test if 
	# PyV8.py(c) exists in PYTHONPATH before importing PyV8
	if 'PyV8' in sys.modules:
		# PyV8 was loaded by ST2, create global alias
		if 'PyV8' not in globals():
			globals()['PyV8'] = __import__('PyV8')
			
		return

	loaded = False
	f, pathname, description = imp.find_module('PyV8')
	bin_f, bin_pathname, bin_description = imp.find_module('_PyV8')
	if f:
		try:
			imp.acquire_lock()
			globals()['_PyV8'] = imp.load_module('_PyV8', bin_f, bin_pathname, bin_description)
			globals()['PyV8'] = imp.load_module('PyV8', f, pathname, description)
			imp.release_lock()
			loaded = True
		finally:
			# Since we may exit via an exception, close fp explicitly.
			if f:
				f.close()
			if bin_f:
				bin_f.close()

	if not loaded:
		raise ImportError('No PyV8 module found')

import sublime;
from SublimeJS.core.process import Process
import traceback

class Context():
	_js_logger = None

	def __init__(self, logger):
		self._js_logger = logger;
		try:
			import_pyv8()
		except ImportError as e:
			pass
		self._js_ctx = PyV8.JSContext(self)
		self._use_unicode = should_use_unicode()

	def abspath(self, path):
		return os.path.abspath(path)

	def load_resource(self, path):
		path = os.path.abspath(path)
		try:
			return js_file_reader(path, self._use_unicode)
		except Exception as ex:
			raise ex
	
	def load_js_file(self, path):
		self._js_ctx.enter()
		path = os.path.abspath(path)
		lib = os.path.abspath(os.path.join(os.path.dirname(__file__),'../js',os.path.basename(path)));

		try:
			code = js_file_reader(path, self._use_unicode)
		except:
			code = js_file_reader(lib, self._use_unicode)
			
		try:
			code = "(function(global){function require(e){e=e.replace(/\.js$/,'');global.__modules=global.__modules||{};var p=global.__modules[global.abspath(__dirname+'/'+e+'.js')];if(p){return p};p=load_js_file(__dirname+'/'+e+'.js');return p};require.toString=function(){return 'function () { [native code] }'};function load_settings(res){try{return JSON.parse(global.load_resource(__dirname+'/'+res))}catch(ex){throw new Error(ex.message)}};load_settings.toString=function(){return 'function () { [native code] }'};var __filename,__dirname,module={exports:{}},exports=module.exports;(function(){__dirname='" + os.path.dirname(path).replace("\\","\\\\") + "';__filename='" + path.replace("\\","\\\\") + "';})();\n" + code + "\n\n;console.log('Load module:'+__filename);global.__modules[__filename]=module.exports;return global.__modules[__filename];})(this);";
			r = self._js_ctx.eval(code)
			return r
		except IOError as ex:
			# traceback.print_exc(file=sys.stdout)
			raise ex
		except Exception as ex:
			traceback.print_exc(file=sys.stdout)
			raise ex
		finally:
			self._js_ctx.leave()

	def call(self, func, args = []):
		self._js_ctx.enter()

		try:
			self.ARGS__ = args
			r = self._js_ctx.eval("(function(global){var args=[];for(var i in global.ARGS__){args[i]=global.ARGS__[i]};var ret="+func+".apply("+('.'.join(func.split('.')[0:-1]) or 'global')+", args);delete global.ARGS__;return ret})(this);")
			return r
		except PyV8.JSError as ex:
			raise ex
		finally:
			self._js_ctx.leave()

	def eval(self, code):
		self._js_ctx.enter()
		
		try:
			r = self._js_ctx.eval(code)
			return r
		except PyV8.JSError as ex:
			raise ex
		finally:
			self._js_ctx.leave()

	@property 
	def process(self):
		return Process()
	
