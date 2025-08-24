import cv2 as cv

from Utilitarios import Utilitarios

class RenderizaImagem:

    def __init__(self, *, imagem, callbackQuadroSelecionado, callbackFecharImagem, callbackViewCrua, callbackViewSetores, callbackViewContagem, callbackExportarContagem, fonteTexto, escalaTexto, corTexto, espessuraTexto, corLinha, espessuraLinha, opacidadeLinha, opacidadeSetorContabilizado):
        self.__imagem = imagem
        self.__callbackQuadroSelecionado = callbackQuadroSelecionado
        self.__callbackFecharImagem = callbackFecharImagem
  
        self.__fonteTexto = fonteTexto 
        self.__escalaTexto = escalaTexto 
        self.__corTexto = corTexto 
        self.__espessuraTexto = espessuraTexto
        self.__corLinha = corLinha 
        self.__espessuraLinha = espessuraLinha 
        self.__opacidadeLinha = opacidadeLinha
        self.__opacidadeSetorContabilizado = opacidadeSetorContabilizado
        self.__callbackViewCrua = callbackViewCrua
        self.__callbackViewSetores = callbackViewSetores
        self.__callbackViewContagem = callbackViewContagem
        self.__callbackExportarContagem = callbackExportarContagem

    def renderizaImagem(self):
        self.__mostraImagem(
            img = self.__imagem.obtemImg(),
            dictWaitKey = {
                'q': self.__fecharImagem,
                'f': self.__defineViewSetores,
                's': self.__callbackExportarContagem
            }
        )

    def renderizaImagemComSetores(self):
        copiaImg = self.__renderizaBordas(self.__imagem.obtemImg())
        copiaImg = self.__renderizaSetores(copiaImg)
        self.__mostraImagem(
            img = copiaImg,
            mouseEvent = self.__mouseEventCallback,
            dictWaitKey = {
                'q': self.__fecharImagem,
                'f': self.__defineViewCrua,
                'r': self.__defineViewContagem,
                's': self.__callbackExportarContagem
            }
        )

    def renderizaImagemComContagem(self):
        copiaImg = self.__renderizaBordas(self.__imagem.obtemImg())
        copiaImg = self.__renderizaSetores(copiaImg)
        copiaImg = self.__renderizaContagem(copiaImg)
        self.__mostraImagem(
            img = copiaImg,
            mouseEvent = self.__mouseEventCallback,
            dictWaitKey = {
                'q': self.__fecharImagem,
                'r': self.__defineViewSetores,
                's': self.__callbackExportarContagem
            }
        )

    def __mostraImagem(self, *, img, dictWaitKey = {}, mouseEvent = None):
        self.__imagemEstaAberta = True
        cv.namedWindow("Imagem", cv.WND_PROP_FULLSCREEN)
        cv.setWindowProperty("Imagem", cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        cv.imshow("Imagem", img)

        if mouseEvent is not None:
            cv.setMouseCallback("Imagem", mouseEvent)

        while self.__imagemEstaAberta:
            key = chr(cv.waitKey(1000) & 0xFF)
            if key in dictWaitKey:
                dictWaitKey[key]()
                
 
    def __renderizaBordas(self, img):
        copiaImg = img.copy()
        alturaImg, larguraImg = img.shape[:2]

        posY = self.__imagem.obtemSaltoLinha()
        while posY < alturaImg:
            cv.line(copiaImg, (0, posY), (larguraImg, posY), self.__corLinha, self.__espessuraLinha)
            posY += self.__imagem.obtemSaltoLinha()
        
        posX = self.__imagem.obtemSaltoColuna()
        while posX < larguraImg:
            cv.line(copiaImg, (posX, 0), (posX, alturaImg), self.__corLinha, self.__espessuraLinha)
            posX += self.__imagem.obtemSaltoColuna()

        return Utilitarios.renderizaComOpacidade(imgOriginal=img, imgModificada=copiaImg, opacidade=self.__opacidadeLinha)

    def __renderizaSetores(self, img):
        setores = self.__imagem.obtemSetores()
        copiaImg = img.copy()
        for setor in setores:
            if setor.obtemContabilizado():    
                coordenadaInicial, coordenadaFinal = setor.obtemCoordenadas()
                cv.rectangle(copiaImg, coordenadaInicial, coordenadaFinal, self.__corLinha, -1)
        img = Utilitarios.renderizaComOpacidade(imgOriginal=img, imgModificada=copiaImg, opacidade=self.__opacidadeSetorContabilizado)
        return img
    
    def __renderizaContagem(self, img):
        setores = self.__imagem.obtemSetores()
        copiaImg = img.copy()
        for setor in setores:
            if setor.obtemContabilizado():
                coordenadaInicial, coordenadaFinal = setor.obtemCoordenadas()
                cv.rectangle(copiaImg, coordenadaInicial, (coordenadaInicial[0] + 30, coordenadaInicial[1] + 30), (0, 0, 0), -1)
                cv.putText(
                        copiaImg,
                        str(setor.obtemContagem()),
                        (coordenadaInicial[0], coordenadaInicial[1] + 20),
                        self.__fonteTexto,
                        self.__escalaTexto,
                        self.__corTexto, 
                        self.__espessuraTexto, 
                        cv.LINE_AA
                    )
        img = Utilitarios.renderizaComOpacidade(imgOriginal=img, imgModificada=copiaImg, opacidade=1)
        return img


    def __mouseEventCallback(self, event, x, y, *_):
        if event == cv.EVENT_LBUTTONDOWN:
            self.__imagemEstaAberta = False
            self.__callbackQuadroSelecionado(x, y)

    def __fecharImagem(self):
        self.__imagemEstaAberta = False
        self.__callbackFecharImagem()

    def __defineViewCrua(self):
        self.__imagemEstaAberta = False
        self.__callbackViewCrua()
    
    def __defineViewSetores(self):
        self.__imagemEstaAberta = False
        self.__callbackViewSetores()
    
    def __defineViewContagem(self):
        self.__imagemEstaAberta = False
        self.__callbackViewContagem()