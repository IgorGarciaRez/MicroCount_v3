import os
from glob import glob
import re
import cv2

from controllers.GerenciaImagem import GerenciaImagem
from controllers.SelecionaImagem import SelecionaImagem

from Settings import *

class Sistema:

    def __init__(self):
    
        try:
            #caminhoImg = SelecionaImagem.selecionaImagem(extensoesValidas = EXTENSOES_VALIDAS)
            caminhoImg = r'C:\Users\Igor\Documents\microCount_v2-main\assets\16.2 - 1.jpg'
            gerenciaImagem = GerenciaImagem(
                caminhoImg = caminhoImg,
                caminhoExportacao = os.path.join(os.getcwd(), CAMINHO_EXPORTAR_CONTAGEM),
                contagemPadrao = VALOR_CONTAGEM_PADRAO,
                porcentagemSetor = PORCENTAGEM_SETOR, 
                zoomSetor = ZOOM_SETOR,
                corPrimaria = COR_PRIMARIA,
                corSecundaria = COR_SECUNDARIA, 
                espessuraDivisoria = ESPESSURA_DIVISORIA,
                opacidadeDivisoria = OPACIDADE_DIVISORIA,
                opacidadeSetorContabilizado = OPACIDADE_SETOR_CONTABILIZADO,
                fonteTexto = FONTE_ROTULO_SETOR,
                escalaTexto = ESCALA_ROTULO_SETOR,
                corTexto = COR_ROTULO_SETOR,
                espessuraTexto = ESPESSURA_ROTULO_SETOR,
                opacidadeMarcacao = OPACIDADE_MARCACAO,
                raioMarcacao = RAIO_MARCACAO
            )
            gerenciaImagem.contagem()
        except Exception as err:
            print(err)       