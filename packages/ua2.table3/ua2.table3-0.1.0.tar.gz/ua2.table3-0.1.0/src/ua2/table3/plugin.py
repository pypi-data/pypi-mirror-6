class StopProcessing(Exception):
    def __init__(self, value):
        self.value = value


class BasePlugin(object):
    """
    Can have next methods:
      process_request(self, request)
      process_response(self, request)
      process_row(self, request, row)
    """

