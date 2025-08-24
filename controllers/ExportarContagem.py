import os
import cv2 as cv
import csv

class ExportarContagem:

    camposCsv = ["nome_arquivo", "contagem_manual", "contagem_ia", "coordenada_inicio", "coordenada_fim"]

    @staticmethod
    def removeContagemAnterior(caminhoPastaExportacao):
        try:
            for elemento in os.listdir(caminhoPastaExportacao):
                caminhoElemento = os.path.join(caminhoPastaExportacao, elemento)

                if(os.path.isdir(caminhoElemento)):
                    ExportarContagem.removeContagemAnterior(caminhoPastaExportacao=caminhoElemento)
                else:
                    os.remove(caminhoElemento)

            os.rmdir(caminhoPastaExportacao)

        except Exception as err:
            print(err)

    def __init__(self, *, imagem, caminhoExportacao, contagemPadrao) -> None:
        self.__imagem = imagem
        self.__caminhoExportacao = caminhoExportacao
        self.__contagemPadrao = contagemPadrao

    def __exportarImagem(self, caminhoImg, img):
        cv.imwrite(caminhoImg, img)

    def __exportarCsv(self, caminhoArq, dadosCsv):
        with open(caminhoArq, mode='w', encoding='utf-8') as arquivoCsv:
            escritorArq = csv.DictWriter(arquivoCsv, fieldnames=ExportarContagem.camposCsv)
            escritorArq.writeheader()
            escritorArq.writerows(dadosCsv)

    def exportaContagem(self):

        nomeImg = self.__imagem.obtemNomeImg()
        extensaoImg = self.__imagem.obtemExtensaoImg()

        caminhoPastaExportacao = os.path.join(self.__caminhoExportacao, nomeImg)

        if(os.path.isdir(caminhoPastaExportacao)):
            ExportarContagem.removeContagemAnterior(caminhoPastaExportacao=caminhoPastaExportacao)
        os.makedirs(caminhoPastaExportacao)

        img = self.__imagem.obtemImg()
        dadosCsv = []

        for setor in self.__imagem.obtemSetores():

            coordendasSetor = setor.obtemCoordenadas()
            nomeSetor = f"setor_{setor.obtemId()}.{extensaoImg}"

            contagemIA = setor.obtemContagem() if setor.obtemContabilizado() else self.__contagemPadrao
            
            contagemManual = setor.obtemContagemManual() if hasattr(setor, "obtemContagemManual") else 0

            dadosCsv.append({
                "nome_arquivo": nomeSetor,
                "contagem_manual": contagemManual,
                "contagem_ia": contagemIA,
                "coordenada_inicio": coordendasSetor[0],
                "coordenada_fim": coordendasSetor[1]
            })

            imgQuadro = img[coordendasSetor[0][1] : coordendasSetor[1][1] + 1, coordendasSetor[0][0] : coordendasSetor[1][0] + 1]
            self.__exportarImagem(os.path.join(caminhoPastaExportacao, nomeSetor), imgQuadro)

        self.__exportarImagem(os.path.join(caminhoPastaExportacao, f"{nomeImg}.{extensaoImg}"), img)
        self.__exportarCsv(os.path.join(caminhoPastaExportacao, f"contagem.csv"), dadosCsv)
        print("Csv exportado para /export")