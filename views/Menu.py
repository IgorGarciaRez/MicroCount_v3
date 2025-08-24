from Utilitarios import Utilitarios 
from .OpcaoMenu import OpcaoMenu

class Menu:

    def __init__(self, *, titulo, opcoes, larguraMenu = 50, caractereEspacamento = '*'):
        self.__titulo = titulo
        self.__opcoes = tuple(
            (
                OpcaoMenu(
                    rotulo=f"{i + 1}) {opRotulo}", 
                    callback=opCallback, 
                ) for i, (opRotulo, opCallback) in enumerate(opcoes)
            )
        )
        self.__larguraMenu = larguraMenu
        self.__caractereEspacamento = caractereEspacamento
    
    def __tituloComoString(self):
        tamPreenchimento = self.__larguraMenu - len(self.__titulo) - 2
        preenchimento = self.__caractereEspacamento * (tamPreenchimento//2)
        return f"{preenchimento} {self.__titulo} {preenchimento}"

    def __opcoesComoString(self):

        strOpcoes = ""
        for opMenu in self.__opcoes:
            strOpcoes += f"{str(opMenu)}\n"
        return strOpcoes

    def mostraMenu(self):

        opValida = False
        strMenu = f"{self.__tituloComoString()}\n\n{self.__opcoesComoString()}"
        strMenu += "\n\n Escolha uma opcao:     "
        
        while not opValida:
            Utilitarios.limparTerminal()

            opEscolhida = input(strMenu).strip()
            if opEscolhida:
                opEscolhida = int(opEscolhida) 

                if(1 <= opEscolhida <= len(self.__opcoes)):
                    opValida = True
                    callback = self.__opcoes[opEscolhida - 1].callback
                    if callback is not None:
                        callback()
                
                else:
                    input("\nOperacao invalida.\nEnter para continuar...")
    