"""
Este é um método para listas aninhadas!
"""
def print_lol(alista):
    """
    Este método recebe uma lista como parametro e faz todo o 
    processamento
    """
    for each in alista:
        if isinstance (each, list):
            print_lol(each)
        else:
            print (each)
