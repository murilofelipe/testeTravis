import unittest
import parser
import subprocess

# variaveis globais
ilexema = 0  ## indice do lexema
linhas = 0  ## contador de linhas
lexema = ""  ## lexema
arquivo = ""
FIM = 0

def verificar_sintaticamente(resultado):
    if resultado == "< OK - Sucesso >":
        return True
    else:
        return False

class VerificarPangramaTests(unittest.TestCase):
    def test_metodo_de_teste(self):
        pass


    def test_retorna_verdadeiro_quando_frase_pangrama(self):
        # Arrange
        nome_arquivo = "teste1.pas"
        farse = parser.parser(nome_arquivo)

        # Act
        programa_estah_correto = verificar_sintaticamente(frase)

        # Assert

        self.assertTrue(programa_estah_correto)



if __name__ == '__main__':
    arq = "teste1.pas"  ##input()   ## ARRUMAR AQUI NO FIM DO TRABALHO ********************
    f = open(arq, 'r')
    texto = f.readlines()  ## lista de linhas  do texto

    strTexto = parser.textoToString(texto)  ## vetor de caracteres do texto inteiro já maiusculo
    arquivo = strTexto
    tamTexto = len(arquivo)
    linhas = 2
    token = ""
    FIM = tamTexto
    parser.parser()


    f.close()
