from pipeline import Screen

		
class StopProcessingHandler(Screen):
	def Execute(self, msg):
		if msg.StopProcessing:
			return msg
		else:
			return self.target(msg)