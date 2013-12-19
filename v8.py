#coding: utf8

import sublime, sublime_plugin
import sys, os

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
PACKAGES_PATH = sublime.packages_path() or os.path.dirname(BASE_PATH)
if(BASE_PATH not in sys.path):
	sys.path += [BASE_PATH] + [os.path.join(BASE_PATH, 'lib')] + [os.path.join(BASE_PATH, 'SublimeJS/core')]

import SublimeJS.loader.pyv8loader as pyv8loader

from SublimeJS.core.context import Context, import_pyv8
from SublimeJS.core.context import js_file_reader as _js_file_reader
from SublimeJS.loader.pyv8loader import LoaderDelegate

is_python3 = sys.version_info[0] > 2

# JS context
ctx = None

# sublime-v8 Settings
# settings = None

# Default ST settings
# user_settings = None

def is_st3():
	return sublime.version()[0] == '3'


#######################
# Reload Lib

# The original idea is borrowed from 
# https://github.com/wbond/sublime_package_control/blob/master/package_control/reloader.py 

import imp

reload_mods = []
for mod in sys.modules:
	if mod.startswith('SublimeJS') and sys.modules[mod] != None:
		reload_mods.append(mod)

mods_load_order = [
	'SublimeJS.core.semver',
	'SublimeJS.loader.pyv8loader',
	'SublimeJS.core.file',
	'SublimeJS.core.http',
	'SublimeJS.core.process',
	'SublimeJS.core.child_process',
	'SublimeJS.core.fs',
	'SublimeJS.core.context',
]

for mod in mods_load_order:
	if mod in reload_mods:
		m = sys.modules[mod]
		if 'on_module_reload' in m.__dict__:
			m.on_module_reload()
		imp.reload(sys.modules[mod])

def convert(obj):	
	from PyV8 import JSObject, JSArray, JSFunction
	
	if type(obj) == JSArray:
		return [convert(v) for v in obj]
	
	if type(obj) == JSObject:
		return dict([[str(k), convert(obj.__getattr__(str(k)))] for k in 
obj.__members__])
		
	return obj

##################################
# Global Events	
class EventDispatcher(sublime_plugin.EventListener):  
	def on_new(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['new', view])
		return True
	def on_clone(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['clone', view])
		return True   
	def on_load(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['load', view])
		return True
	def on_pre_close(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['pre_close', view])
		return True			   	
	def on_close(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['close', view])
		return True	
	def on_pre_save(self, view):  
		if(ctx):
			return ctx.call('global.E.emit',['pre_save', view])
		return True 
	def on_post_save(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['post_save', view])
		return True
	def on_modified(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['modified', view])
		return True
	def on_selection_modified(self, view):
		if(ctx):
			return ctx.call('global.E.emit',['selection_modified', view])
		return True		
	def on_activated(self, view):
		if(ctx):
			ctx.call('global.E.emit',['activated', view]) 
			ctx.call('global.E.emit',['focus', view])
		return True			
	def on_deactived(self, view):
		if(ctx):
			ctx.call('global.E.emit',['deactived', view]) 
			ctx.call('global.E.emit',['blur', view])
		return True		
	def on_text_command(self, view, command_name, args):	
		if(ctx):
			return ctx.call('global.E.emit',['text_command', view, command_name, args])
		return (command_name, args)
	def on_window_command(self, window, command_name, args):
		if(ctx):
			return ctx.call('global.E.emit',['window_command', window, command_name, args])
		return (command_name, args)
	def post_text_command(self, view, command_name, args):
		if(ctx):
			return ctx.call('global.E.emit',['post_text_command', view, command_name, args])
		return True
	def post_window_command(self, window, command_name, args):
		if(ctx):
			return ctx.call('global.E.emit',['post_window_command', window, command_name, args])
		return True	
	def on_query_context(self, view, key, operator, operand, match_all):
		if(ctx):
			return ctx.call('global.E.emit',['query_context', view, key, operator, operand, match_all])
		return True				
	def on_query_completions(self, view, prefix, locations):
		if(ctx):
			ctx._js_ctx.enter()
			ret = convert(ctx.call('global.E.on_query_completions',[view, prefix, locations]))
			ctx._js_ctx.leave()
			return ret
		return None	

##########################
# Base Class of JSCommand
class JSTextCommand(sublime_plugin.TextCommand):
	def __init__(self, view):
		self.view = view
	def run(self, edit, args=None):
		command = self.__class__.__name__[0:-7].lower()
		ctx.call('global.runCommand', [command, self.view, edit, args]);
		# ctx.load_js_file(os.path.join(BASE_PATH, mod), {'view':self.view, 'edit': edit})

class JSWindowCommand(sublime_plugin.WindowCommand):
	def __init__(self, window):
		self.window = window
	def run(self, args=None):
		command = self.__class__.__name__[0:-7].lower()
		ctx.call('global.runCommand', [command, self.window, args]);

class JSApplicationCommand(sublime_plugin.ApplicationCommand):
	def run(self, args=None):
		command = self.__class__.__name__[0:-7].lower()
		ctx.call('global.runCommand', [command, args]);

class HelloWorldCommand(JSTextCommand):
	'''demo'''
	pass

############################
def init():
	"Init sublime-v8 engine"

	# setup environment for PyV8 loading
	pyv8_paths = [
		os.path.join(PACKAGES_PATH, 'PyV8'),
		os.path.join(PACKAGES_PATH, 'PyV8', pyv8loader.get_arch()),
		os.path.join(PACKAGES_PATH, 'PyV8', 'pyv8-%s' % pyv8loader.get_arch())
	]

	sys.path += pyv8_paths

	# unpack recently loaded binary, is exists
	for p in pyv8_paths:
		pyv8loader.unpack_pyv8(p)

	###################################
	# if you need update PyV8, comment this
	try:
		import PyV8
	except:
		pass
	###################################

	# create JS environment
	delegate = SublimeLoaderDelegate()

	pyv8loader.load(pyv8_paths[1], delegate) 

class SublimeLoaderDelegate(LoaderDelegate):
	load_cache = []
	def __init__(self, settings=None):

		if settings is None:
			settings = {}
			#for k in ['http_proxy', 'https_proxy', 'timeout']:
			#	if user_settings.has(k):
			#		settings[k] = user_settings.get(k, None)

		LoaderDelegate.__init__(self, settings)
		self.state = None
		self.message = 'Loading PyV8 binary, please wait'
		self.i = 0
		self.addend = 1
		self.size = 8

	def on_start(self, *args, **kwargs):
		self.state = 'loading'

	def on_progress(self, *args, **kwargs):
		if kwargs['progress'].is_background:
			return

		before = self.i % self.size
		after = (self.size - 1) - before
		msg = '%s [%s=%s]' % (self.message, ' ' * before, ' ' * after)
		if not after:
			self.addend = -1
		if not before:
			self.addend = 1
		self.i += self.addend

		sublime.set_timeout(lambda: sublime.status_message(msg), 0)

	def on_complete(self, *args, **kwargs):
		self.state = 'complete'

		if kwargs['progress'].is_background:
			return

		sublime.set_timeout(self.on_ready, 0)

	def on_ready(self):
		sublime.status_message('PyV8 binary successfully loaded')
		if(not ctx):
			globals()['ctx'] = JSCore(self.log)
			from PyV8 import JSClass, JSObject, JSArray, JSFunction
			ctx.JSClass = lambda obj: JSClass(convert(obj))
			ctx.JSObject = lambda obj: JSObject(convert(obj))
			ctx.JSArray = lambda obj: JSArray(convert(obj))
			ctx.JSFunction = lambda obj: JSFunction(convert(obj))
			ctx.load_js_file(os.path.join(BASE_PATH, "SublimeJS/js/core.js"))
			if('js_loading_queue' in globals()):
				for i in globals()['js_loading_queue']:
					ctx.load_js_file(i)

		# if('Update_JS' not in globals() or globals()['Update_JS'] == True):
		#	globals()['Update_JS'] = False
		#	ctx.reload()

	def on_error(self, exit_code=-1, thread=None):
		self.state = 'error'
		sublime.set_timeout(lambda: show_pyv8_error(exit_code), 0)

	def setting(self, name, default=None):
		"Returns specified setting name"
		return self.settings.get(name, default)

	def log(self, message):
		print('JS: %s' % message)

def plugin_loaded():
	sublime.set_timeout(init, 200)

##################
# Init plugin
if not is_python3:
	init()

class Console:
	def __init__(self, logger):
		self.logger = logger;
	def log(self, msg):
		self.logger(msg);

import hashlib, urllib

class JSCore(Context):
	_reload = False
	def __init__(self, logger):
		self.console = Console(logger);
		Context.__init__(self, logger)

	def registerCommand(self, name, commandType):
		name = name + 'Command'
		fullName = '<' + commandType + '>SublimeJS.v8.' + name;
		if(fullName not in globals()):
			if(commandType == 'TextCommand'):
				globals()[fullName] = type(name, (JSTextCommand,), {})
			if(commandType == 'WindowCommand'):
				globals()[fullName] = type(name, (JSWindowCommand,), {})
			if(commandType == 'ApplicationCommand'):
				globals()[fullName] = type(name, (ApplicationCommand,), {})
			if(not self._reload):
				sublime.set_timeout(lambda:sublime_plugin.reload_plugin('SublimeJS.v8'), 50)
				self._reload = True

	@property 
	def sublime(self):
		return sublime

	def reload(self):
		sublime_plugin.reload_plugin('SublimeJS.v8');
		
	def md5(self, str):
		return hashlib.md5(str).hexdigest()

class JS:
	_base_dir = None

	def __init__(self, base):
		self._base_dir = base;

	def boot(self, file = 'index.js'):
		if(globals()['ctx']):
			globals()['ctx'].load_js_file(os.path.join(self._base_dir, file))
		else:
			if(not 'js_loading_queue' in globals()):
				globals()['js_loading_queue'] = []
			globals()['js_loading_queue'].append(os.path.join(self._base_dir, file))

def getContext():
	return globals()['ctx']
