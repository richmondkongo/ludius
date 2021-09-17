from ludius_ai import IA as ia

class IA(ia):

    #Team modify this
    name = "ARandomI"
    
    def __init__(self,position, gameSize):
        print('----------------------------------------------------------------------------{}----------------------------------------------------------------------------'.format(self.name))
        ia.__init__(self,position, gameSize)