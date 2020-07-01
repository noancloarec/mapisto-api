from werkzeug.exceptions import Conflict

class MapistoException(Conflict):
    def __init__(self, description, response):
        assert isinstance(description, str)
        assert isinstance(response, dict)
        super().__init__(description, response)
