import logging
moduleLogger = logging.getLogger(__name__)
from threading import _Event


class Bucket(_Event):
	def __init__(self):
		self.callbacks = []
		_Event.__init__(self)
		self.msg = None
		
	def Tap(self, callback):
		self.callbacks.append(callback)
		
	def Fill(self, msg):
		self.msg = msg
		_Event.set(self)
		for callback in self.callbacks:
			callback(msg)
		return msg
				
	def Wait(self, timeout = None):
		if _Event.wait(self, timeout):
			return self.msg
		else:
			return False
		
	def Check(self):
		return self.Wait(0)