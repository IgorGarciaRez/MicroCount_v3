import cv2 as cv

from Utilitarios import Utilitarios
from controllers import DetectorAuto

class RenderizaSetor:

    def __init__(
        self, *,
        imagem,
        callbackMarcarElemento,
        callbackEncerrarSetor,
        opacidadeMarcacao,
        raioMarcacao,
        corMarcacao,
        zoomSetor,
        ehNovaRenderizacao,
        resetaPontosSetor,
        callbackUndo=None
    ):
        self.__imagem = imagem
        self.__callbackEncerrarSetor = callbackEncerrarSetor
        self.__callbackMarcarElemento = callbackMarcarElemento
        self.__opacidadeMarcacao = opacidadeMarcacao
        self.__zoomSetor = zoomSetor
        self.__raioMarcacao = raioMarcacao
        self.__corMarcacao = corMarcacao
        self.__ehNovaRenderizacao = ehNovaRenderizacao
        self.__imgZoom = None
        self.__resetaPontosSetor = resetaPontosSetor
        self.__mostrarIA = True
        self.__callbackUndo = callbackUndo

        self.__callbackSalvar = None

        self.__pontosIA_zoom = None

        self.__last_qtd_manual = 0
        self.__last_qtd_ia = 0

    def setCallbackSalvar(self, cb):
        """Controller/Estado injeta aqui a função que grava CSV/modelo quando fecha o setor (q)."""
        self.__callbackSalvar = cb

    def __mostraSetor(self, *, img):
        self.__imagemEstaAberta = True
        cv.imshow("Setor", img)
        cv.setMouseCallback("Setor", self.__mouseEventCallback)
        while self.__imagemEstaAberta:
            key = chr(cv.waitKey(1000) & 0xFF)
            if key == 'q':
                if callable(self.__callbackSalvar):
                    try:
                        self.__callbackSalvar(
                            qtd_manual=self.__last_qtd_manual,
                            qtd_ia=self.__last_qtd_ia
                        )
                    except Exception as _:
                        pass
                self.__callbackEncerrarSetor()
                break
            elif key == 'r':
                self.__resetaPontosSetor()
                break
            elif key == 'a':
                self.__mostrarIA = not self.__mostrarIA
                break
            elif key == 'u' and self.__callbackUndo is not None:
                self.__callbackUndo()
                break

    def renderizaSetor(self, pontosSetor, pontosAuto=None):
        """
        pontosSetor: pontos manuais já no espaço do ZOOM (pois vêm dos cliques na janela "Setor")
        pontosAuto:  opcional; se None, a view calcula IA no ROI original e converte para o ZOOM
        """
        if self.__ehNovaRenderizacao():
            roi = self.__imagem.obtemImgSetorAtual()
            self.__imgZoom = self.__renderizaZoom(roi)
            self.__pontosIA_zoom = None

        pts_auto_zoom = None
        if pontosAuto is not None:
            pts_auto_zoom = list(pontosAuto)
        else:
            if self.__mostrarIA and self.__pontosIA_zoom is None:
                try:
                    roi = self.__imagem.obtemImgSetorAtual()
                    #Vizualizar passos como TRUE -> Abre várias janelas de todos os processos para identificação das bactérias
                    pts_auto = DetectorAuto.detectar_colonias(roi, visualizar_passos=False) 
                    z = self.__zoomSetor
                    self.__pontosIA_zoom = [(int(x * z), int(y * z)) for (x, y) in pts_auto]
                except Exception:
                    self.__pontosIA_zoom = []
            pts_auto_zoom = self.__pontosIA_zoom

        copia = self.__imgZoom.copy()

        # IA (verde) – opcional
        if self.__mostrarIA and pts_auto_zoom:
            for (x, y) in pts_auto_zoom:
                cv.circle(copia, (x, y), max(2, self.__raioMarcacao - 1), (0, 255, 0), -1)

        # Manual (vermelho)
        for (x, y) in pontosSetor:
            cv.circle(copia, (x, y), self.__raioMarcacao, self.__corMarcacao, -1)

        qtd_manual = len(pontosSetor)
        qtd_ia = len(pts_auto_zoom) if pts_auto_zoom is not None else 0
        self.__last_qtd_manual = qtd_manual
        self.__imagem.defineContagemSetorAtual(qtd_manual)

        # ---------------------------- Se quiser usar a IA para contagem ------------------------
        #self.__imagem.defineContagemSetorAtual(qtd_manual+qtd_ia)
        self.__last_qtd_ia = qtd_ia

        txt = [f"Manual: {qtd_manual}"]
        if pts_auto_zoom is not None:
            txt.append(f"IA: {qtd_ia}")
            txt.append(f"Δ: {abs(qtd_manual - qtd_ia)}")

        largura_badge = 10 + (max(len(t) for t in txt) * 8 if txt else 170)
        altura_badge = 10 + 18 * len(txt)
        cv.rectangle(copia, (5, 5), (5 + largura_badge, 5 + altura_badge), (0, 0, 0), -1)
        for i, t in enumerate(txt):
            cv.putText(copia, t, (10, 25 + i * 18), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)

        self.__mostraSetor(
            img=Utilitarios.renderizaComOpacidade(
                imgOriginal=self.__imgZoom,
                imgModificada=copia,
                opacidade=self.__opacidadeMarcacao
            )
        )

    def __renderizaZoom(self, img):
        alturaImg, larguraImg = img.shape[:2]
        novaAltura, novaLargura = self.__zoomSetor * alturaImg, self.__zoomSetor * larguraImg
        imgZoom = cv.resize(img, (novaLargura, novaAltura), interpolation=cv.INTER_LANCZOS4)
        return imgZoom

    def __renderizaMarcacoes(self, img, pontosSetor):
        copiaImg = img.copy()
        for ponto in pontosSetor:
            cv.circle(copiaImg, ponto, self.__raioMarcacao, self.__corMarcacao, -1)
        return Utilitarios.renderizaComOpacidade(
            imgOriginal=img,
            imgModificada=copiaImg,
            opacidade=self.__opacidadeMarcacao
        )

    def __mouseEventCallback(self, event, x, y, *_):
        if event == cv.EVENT_LBUTTONDOWN:
            self.__imagemEstaAberta = False
            self.__callbackMarcarElemento(x, y)
