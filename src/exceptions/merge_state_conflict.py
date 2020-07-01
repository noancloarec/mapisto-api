from .mapisto_exceptions import MapistoException
class MergeStateConflictException(MapistoException):
    def __init__(self, description,  territories_impacted):
        super().__init__(description, {'territories_impacted' : territories_impacted} )
