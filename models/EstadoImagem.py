
import cv2 as cv

from .Estado import Estado
from views import RenderizaImagem
from controllers.ExportarContagem import ExportarContagem

class EstadoImagem(Estado):

    def __init__(self, *, imagem, contagemPadrao, encerrarExecucao, callbackNavegarSetor, fonteTexto, escalaTexto, corTexto, espessuraTexto, corLinha, espessuraLinha, opacidadeLinha, opacidadeSetorContabilizado, caminhoExportacao):
        self.__imagem = imagem
        self.__renderizaImagem = RenderizaImagem(
            imagem = imagem, 
            callbackQuadroSelecionado = self.__selecionarQuadro,
            callbackFecharImagem = encerrarExecucao,
            fonteTexto = fonteTexto,
            escalaTexto = escalaTexto,
            corTexto = corTexto,
            espessuraTexto = espessuraTexto,
            corLinha = corLinha,
            espessuraLinha = espessuraLinha,
            opacidadeLinha = opacidadeLinha,
            opacidadeSetorContabilizado = opacidadeSetorContabilizado,
            callbackViewCrua = lambda : self.__defineModoVisualizacao('crua'),
            callbackViewSetores = lambda : self.__defineModoVisualizacao('setores'),
            callbackViewContagem = lambda : self.__defineModoVisualizacao('contagem'),
            callbackExportarContagem = self.__exportarContagem
        )
        self.__exportaContagem = ExportarContagem(
            imagem=imagem,
            caminhoExportacao = caminhoExportacao,
            contagemPadrao = contagemPadrao
        ) 
        self.__callbackNavegarSetor = callbackNavegarSetor
        self.__modoVisualizacao = 'contagem'
        self.__dictVisualizacao = {
            'crua': self.__renderizaImagem.renderizaImagem,
            'setores': self.__renderizaImagem.renderizaImagemComSetores,
            'contagem': self.__renderizaImagem.renderizaImagemComContagem
        }
    
    def __exportarContagem(self):
        self.__exportaContagem.exportaContagem()

    def __selecionarQuadro(self, x_event, y_event):
        setorSelecionado = ((y_event // self.__imagem.obtemSaltoLinha()) * self.__imagem.obtemNumColunas()) + (x_event // self.__imagem.obtemSaltoColuna())
        self.__imagem.defineSetorAtual(setorSelecionado)

        if self.__imagem.obtemSetorSelecionado().obtemContabilizado():
            self.__imagem.resetaContagemSetorAtual()
        else:
            self.__callbackNavegarSetor()
        

    def __defineModoVisualizacao(self, modoVisualizacao):
        if modoVisualizacao in self.__dictVisualizacao:
            self.__modoVisualizacao = modoVisualizacao

    def iniciarEstado(self):
        pass

    def emExecucao(self):
        self.__dictVisualizacao[self.__modoVisualizacao]()
    
    def sairEstado(self):
        cv.destroyWindow("Imagem")