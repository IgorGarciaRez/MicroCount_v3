class OpcaoMenu:

    def __init__(self, *, rotulo, callback):

        self.rotulo = rotulo
        self.callback = callback
    
    def __str__(self):
        return self.rotulo