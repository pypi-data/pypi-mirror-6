# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        TesteClasseCDB2.py
# Purpose:      Classe para testes
#
# Author:      MGFac
#
# Created:     24/08/2013
# Copyright:   (c) MGFac 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import CDBClasse

def main():
    arqferiados = 'C:\\Apostilas\\Python\\BCB\\feriados_nacionais.csv'  ## Home Version
    arqCDI = 'C:\\Apostilas\\Python\\BCB\\ProjFinanPy\\CDICetip.pkl'

    #cdb1 = CDBClasse.CDB('001CDBTeste', 1000000.00, 103.5, arqCDI, '01/01/2013', '28/02/2013',
    #    Path_Arquivo = arqferiados)

    cdb1 = CDBClasse.CDB('140911CDB', 1000000.00, 103.1, arqCDI, '14/09/2011', '31/07/2013',
        Path_Arquivo = arqferiados)

    print(type(cdb1))
    #print(cdb1.mro())
    print(cdb1._cCodAplic)
    #print(cdb1._Calc_RendDia())
    #print(cdb1._RelatorioDiario())
    print(cdb1._RelatorioMensal())


if __name__ == '__main__':
    main()
