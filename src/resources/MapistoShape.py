class MapistoShape:
    def __init__(self, d_path:str , precision_in_km:float=None):
        self.d_path = d_path
        self.precision_in_km = precision_in_km
    
    def __str__(self):
        return f'({self.precision_in_km}, "{self.d_path[:10]}...")'
    def equals(self, other):
        assert isinstance(other, MapistoShape)
        return other.d_path==self.d_path and other.precision_in_km==self.precision_in_km