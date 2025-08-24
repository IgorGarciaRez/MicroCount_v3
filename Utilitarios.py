import os
import cv2 as cv

class Utilitarios:

    @staticmethod
    def confirmacaoUsuario(msgConfirmacao = "Pressione enter para continuar..."):
        input(msgConfirmacao)
    
    @staticmethod
    def limparTerminal():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def renderizaComOpacidade(*, imgOriginal, imgModificada, opacidade):
        if opacidade >=1:
            return imgModificada.copy()
        return cv.addWeighted(imgOriginal, 1 - opacidade, imgModificada, opacidade, 0.0)