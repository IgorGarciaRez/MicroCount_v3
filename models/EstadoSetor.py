import cv2 as cv

from .Estado import Estado
from views import RenderizaSetor

class EstadoSetor(Estado):

    def __init__(self, *, imagem, callbackNavegarInput, opacidadeMarcacao, raioMarcacao, corMarcacao, zoomSetor):
        self.__renderizaSetor = RenderizaSetor(
            imagem = imagem,
            callbackMarcarElemento = self.__marcarElemento,
            callbackEncerrarSetor = callbackNavegarInput,
            opacidadeMarcacao = opacidadeMarcacao,
            raioMarcacao = raioMarcacao,
            corMarcacao = corMarcacao,
            zoomSetor = zoomSetor,
            ehNovaRenderizacao = self.obtemNovaRenderizacao,
            resetaPontosSetor = self.resetaPontosSetor
        )

    def obtemNovaRenderizacao(self):
        return self.__novaRenderizacao
    
    def resetaPontosSetor(self):
        self.__pontosSetor = []

    def __marcarElemento(self, x_event, y_event):
        self.__pontosSetor.append((x_event, y_event))
     
    def iniciarEstado(self):
        self.__novaRenderizacao = True
        self.__pontosSetor = []

    def emExecucao(self):
        self.__renderizaSetor.renderizaSetor(list(self.__pontosSetor))
        self.__novaRenderizacao = False
    
    def sairEstado(self):
        cv.destroyWindow("Setor")