class TrakIOException(Exception):
	"""
	Generic TrakIO exception.
	"""
	pass

class TrakIOServiceException(TrakIOException):
    """
    Error thrown from a service call.
    """
    def __init__(self, message, type, details):
        TrakIOException.__init__(self, message)
        self.type=type
        self.details=details