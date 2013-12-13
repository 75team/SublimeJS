import os
import shlex
import subprocess
import threading
import select
import functools

import sublime

class Process:
	def binding(self, module):
		try:
			return __import__('SublimeJS.core.' + module, globals(), locals(), ['*'])
		except:
			return __import__(module, globals(), locals(), ['*'])