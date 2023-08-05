
class GcmServerError(Exception):

    def __init__(self, *args, **kwargs):
        """ Initializes GcmServerError with optional 'response' object """
        self.response = kwargs.pop('response', None)
        super(GcmServerError, self).__init__(*args, **kwargs)
