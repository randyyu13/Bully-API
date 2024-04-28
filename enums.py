from enum import Enum

class Site(Enum):
    COVERS = hash('COVERS')
    BETTINGPROS = hash('BETTINGPROS')

class Sport(Enum):
    NBA = hash('NBA')
    MLB = hash('MLB')
    NHL = hash('NHL')
    NFL = hash('NFL')