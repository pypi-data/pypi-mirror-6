"""
Este é um método para tratamento de listas aninhadas!
"""
def print_lol(alista, nivel):
    """
    Este método recebe uma lista como parametro e faz todo o 
    processamento
    Agora este metodo alem da lista, recebe um parametro inteiro para medir
    o recuo
    """
    for each in alista:
        if isinstance (each, list):
            print_lol(each, nivel)
        else:
            for espaco in range(nivel):
                print ('\t', end='')
            print (each)
