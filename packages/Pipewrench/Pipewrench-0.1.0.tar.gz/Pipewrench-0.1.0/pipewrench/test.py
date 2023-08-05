class Pipeline(object):
	def __init__(self):
		self.filters = {}
	
	def Register(self, filter, *args):
		self.filters[filter] = args
		return self
		
	def Execute(self, message):
		for filter, args in self.filters.iteritems();
			message = filter(args).Execute(message)
		return msg
		
		
class Filter(object):
	def __init__(self, test, test2):
		self.test = test
		self.test2 = test2
		
	def Execute(self, msg):
		print self.test
		print self.test2
		return msg