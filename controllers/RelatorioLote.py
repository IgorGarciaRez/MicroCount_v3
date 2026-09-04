import os
import re

from controllers import DetectorAuto

class RelatorioLote:

    padraoNomeRelatorio = re.compile(r"relatorio_\d+\.pdf")

    def __init__(self, *, imagem, caminhoRelatorios) -> None:
        self.__imagem = imagem
        self.__caminhoRelatorios = caminhoRelatorios

    def __preparaPastaRelatorios(self):
        caminhoPastaImagem = os.path.join(self.__caminhoRelatorios, self.__imagem.obtemNomeImg())
        os.makedirs(caminhoPastaImagem, exist_ok=True)

        for elemento in os.listdir(caminhoPastaImagem):
            if RelatorioLote.padraoNomeRelatorio.fullmatch(elemento):
                os.remove(os.path.join(caminhoPastaImagem, elemento))

        return caminhoPastaImagem

    def geraRelatorios(self):

        caminhoPastaImagem = self.__preparaPastaRelatorios()
        setorOriginal = self.__imagem.obtemSetorAtual()
        relatoriosGerados = 0

        try:
            for setor in self.__imagem.obtemSetores():

                idSetor = setor.obtemId()
                self.__imagem.defineSetorAtual(idSetor)
                caminhoRelatorio = os.path.join(caminhoPastaImagem, f"relatorio_{idSetor:03d}.pdf")

                try:
                    pontosAuto = DetectorAuto.detectar_colonias(
                        self.__imagem.obtemImgSetorAtual(),
                        salvar_pdf_em = caminhoRelatorio
                    )
                    relatoriosGerados += 1
                    print(f"Setor {idSetor:03d}: {len(pontosAuto)} colonias")
                except Exception as err:
                    print(f"Erro ao gerar o relatorio do setor {idSetor}: {err}")
        finally:
            self.__imagem.defineSetorAtual(setorOriginal)

        print(f"{relatoriosGerados} relatorios gerados em {caminhoPastaImagem}")
