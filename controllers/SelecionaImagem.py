import os
from glob import glob
import re

from views import Menu

class SelecionaImagem:

    @staticmethod
    def selecionaImagem(*, extensoesValidas):
        caminhoBase = os.getcwd()
        caminhoRelativo = input(f"{caminhoBase}/").strip()
        caminhoPasta = os.path.normpath(f"{caminhoBase}/{caminhoRelativo}")

        regex = re.compile(r'.*\.(' + "|".join(extensoesValidas) + ')$')

        nomesImagens = [
            os.path.basename(caminhoArquivo) 
            for caminhoArquivo in filter(
                lambda caminhoArquivo: regex.match(caminhoArquivo) and os.path.isfile(caminhoArquivo),
                glob(os.path.join(caminhoPasta, '*'))
            )
        ]
        
        if not nomesImagens:
            raise Exception("Caminho fornecido invalido.\n")
            
        nomeImg = ""
        def defineImagemEscolhida(nomeImgEscolhida):
            nonlocal nomeImg
            nomeImg = nomeImgEscolhida

        menuImagem = Menu(
            titulo = "Escolha uma imagem",
            opcoes= [(opImagens, lambda nome = opImagens : defineImagemEscolhida(nome)) for opImagens in nomesImagens]
        )
        menuImagem.mostraMenu()
        caminhoImg = os.path.join(caminhoPasta, nomeImg)
        return caminhoImg