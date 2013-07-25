from sets import Set

class Commodity:
    "Represents an Individual Commodity"
    def __init__(self,name):
        self.name = name
        
class CommodityDirector:
    "Operations on the Universe of Commodities"
    def __init__(self):
        self.commodities = Set([]);

    def addCommodity(self,name):
        self.commodities.add(name)
        
    def getCommodities(self):
        return self.commodities
