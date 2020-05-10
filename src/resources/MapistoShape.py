class MapistoShape:
    def __init__(self, d_path:str , precision_in_km:float=None):
        self.d_path = d_path
        self.precision_in_km = precision_in_km
    
    def __str__(self):
        return str(
            {
                "d_path" : self.d_path,
                "precision_in_km" : self.precision_in_km
            }
        )
    def equals(self, other):
        return (isinstance(other, MapistoShape) and other.d_path==self.d_path and other.precision_in_km==self.precision_in_km )