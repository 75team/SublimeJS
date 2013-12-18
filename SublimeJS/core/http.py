import urllib.request
import urllib.parse
import threading
import sublime

from PyV8 import JSObject, JSArray, JSFunction
from SublimeJS.v8 import getContext, convert

class Http:
	def request(self, options, callback=None):
		def _call(host, port, auth, method, path, data='', headers={}, callback=None, *args):
			data = urllib.parse.urlencode(data)
			if(auth):
				host = auth + '@' + host
			url = 'http://' + host + ':' + str(port) + path;
			res = None
			try:
				if(method == 'GET' and data != ''):
					url = url + '?' + data
				req = urllib.request.Request(url);

				opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())

				if(method != 'GET'): 
					res = opener.open(req, data)
				else:
					res = opener.open(req) 
			except Exception as ex:
				pass

			if(callback):
				def _callback():
					ctx = getContext()
					ctx._js_ctx.enter()
					callback(res)
					ctx._js_ctx.leave()
			sublime.set_timeout(_callback, 0)			
		
		options = convert(options)

		host = ('hostname' in options and options['hostname']) or ('host' in options and options['host']) or 'localhost'
		port = ('port' in options and options['port']) or 80
		method = ('method' in options and options['method']) or 'GET'
		path = ('path' in options and options['path']) or '/'
		data = ('data' in options and options['data']) or ''
		headers = ('headers' in options and convert(options['headers'])) or {'host': host}
		auth = ('auth' in options and options['auth']) or ''

		#_call(host, port, method, path, data, headers, callback)
		thread = threading.Thread(target=_call, args=(host, port, auth, method, path, data, headers, callback))
		thread.start()	

	def get(self, options, callback=None):
		if(type(options) == str):
			r = urllib.parse.urlparse(options)
			options = {'hostname': r.hostname, 'port': r.port, 'path': r.path, 'method':'GET'}
			if(r.username):
				options.auth = r.username
				if(r.password):
					options.auth = options.auth + ':' + r.password
		
		self.request(options, callback)

def exports():
	return Http()