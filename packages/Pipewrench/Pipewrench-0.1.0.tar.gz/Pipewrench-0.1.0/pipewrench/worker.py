import threading
from Queue import Empty, Queue

class Worker(threading.Thread):
	def __init__(self, pool):
		self.pool = pool
		self.running = threading.Event()
		self.running.set()
		threading.Thread.__init__(self)

	def run(self):
		while self.running.isSet():
			msg = self.pool.getJob()
			if not msg == None:
				msg[0](msg[1])
				
	def join(self):
		self.running.clear()
		threading.Thread.join(self)
		
		
class Pool(object):
	def __init__(self):
		self.queue = Queue()
		self._condition = threading.Condition()
		
	def getJob(self):
		msg = None
		self._condition.acquire()
		try:
			msg = self.queue.get_nowait()
		except:
			self._condition.wait()
		finally:
			self._condition.release()
			
		return msg
			