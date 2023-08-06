# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        CDBClasse.py
# Purpose:     Modulo contendo as Classes bases para trabalhar-se com operações
#               de Renda Fixa (CDB, Debêntures, LFT, NTN-F, etc) do mercado finan-
#               ceiro brasileiro.
#
# Author:      MGFac
#
# Projeto Principal: FinanPy
# Created:     24/08/2013
# Copyright:   (c) MGFac 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pickle

from FinDt import DatasFinanceiras

#================== Inicio Classe TaxTransforms ========================================================
class TaxTransforms():
    '''
    Classe destinada a transformação de Taxas
    '''
    def __init__(self):
        pass

    def CalcTaxDia(CDIDia, ContratoCDI):
        dTax = ((CDIDia -1) * (ContratoCDI / 100.0))
        return dTax
#================== Fim Classe TaxTransforms ========================================================


#================== Inicio Classe RendaFixa ========================================================
class RendaFixa(DatasFinanceiras):
    '''
    Classe base para produtos renda fixa (cdb, debentures, etc)
    '''

    def __init__(self,  ValorAplicado=0,  ContratoCDI=0,  Path_CDI='',  Data_Inicio=None,
        Data_Fim=None,  NumDias=1,  Opt=1,  Path_Arquivo=''):
            self._cValorAplicado = ValorAplicado
            self._cContratoCDI = ContratoCDI
            self._cPath_CDI = Path_CDI
            self._cData_Inicio = Data_Inicio
            self._cData_Fim = Data_Fim
            self._cNumDias = NumDias
            self._cOpt = Opt
            self._cPath_Arquivo = Path_Arquivo
            DatasFinanceiras.__init__(self, self._cData_Inicio,  self._cData_Fim,  self._cNumDias,
                self._cOpt,  self._cPath_Arquivo)
            self._cCDI = self.__UnPickleDic()
            self._cDiario = {}
            self._cMensal = {}


    def __UnPickleDic(self):
        try:
            with open(self._cPath_CDI,  'rb') as rfile:
                return pickle.load(rfile)
        except IOError as Ierr:
            print("Erro de Leitura: ",  str(Ierr))

    def __Calc_RendBrutoDiario(self, SdoAtual, Taxa):
        RBruto = SdoAtual * Taxa
        return RBruto

    def _AliquotaIr(self,  NumDias):
        if NumDias > 0 and NumDias <= 180:
            AliqIr = 0.225
        elif NumDias > 180 and NumDias <= 360:
            AliqIr = 0.200
        elif NumDias > 360 and NumDias <= 720:
            AliqIr = 0.175
        elif NumDias > 720:
            AliqIr = 0.150
        elif NumDias <= 0:
            AliqIr = 0
        return AliqIr


    def __CalcIR(self, NumbDias, RBruto):
        IrAlq = self._AliquotaIr(NumbDias.days)
        IR = RBruto * IrAlq
        return IR

  
    def __Calc_RendLiquidoDiario(self, RBruto, IR):
        RLiq = RBruto - IR
        return RLiq


    def __Calc_RendDia(self):
        SdoAtual = self._cValorAplicado
        RLiqAcum = 0
        NumbDias = self.StrToData(self._cData_Fim) - self.StrToData(self._cData_Inicio)
        DictTabDia = dict(zip(self.Dias(Opt=3)[1:], self.Dias(Opt=3)))
        for dia in self.Dias(Opt=3)[1:]:
            if DictTabDia[dia] in self._cCDI.keys():
                TaxaDia = TaxTransforms.CalcTaxDia(self._cCDI[DictTabDia[dia]], self._cContratoCDI)
                RBrutoDia = self.__Calc_RendBrutoDiario(SdoAtual, TaxaDia)
                IRDia = self.__CalcIR(NumbDias, RBrutoDia)
                RLiquidoDia = self.__Calc_RendLiquidoDiario(RBrutoDia, IRDia)
                RLiqAcum = RLiqAcum + RLiquidoDia
                SdoAtual = SdoAtual + RBrutoDia
                SdoLiqAtual = self._cValorAplicado + RLiqAcum
                self._cDiario.update({dia:{'TaxDia':TaxaDia, 
                                           'RendBrDia':RBrutoDia, 
                                           'IrDia':IRDia, 
                                           'RendLiqDia':RLiquidoDia, 
                                           'SDBrutoDia':SdoAtual, 
                                           'SDLiqDia':SdoLiqAtual}})


    def __Calc_RendMensal(self):
        self.__Calc_RendDia()
        for dia in self.Dias(Opt=3):
            if dia == self._cData_Fim or dia == DatasFinanceiras.subperiodo(self, self.PrimeiroDiaMes(dia), self.UltimoDiaMes(dia), Opt=3)[-1] :
                RendBrutoMensal, IrMensal, RendLiqMensal = 0,0,0
                DUteis = DatasFinanceiras.subperiodo(self, self.PrimeiroDiaMes(dia), self.UltimoDiaMes(dia), Opt=3)
                for subdia in DUteis:
                    if subdia in self._cDiario.keys():
                        RendBrutoMensal, IrMensal, RendLiqMensal = (
                                  RendBrutoMensal + self._cDiario[subdia]['RendBrDia'],
                                  IrMensal + self._cDiario[subdia]['IrDia'],
                                  RendLiqMensal + self._cDiario[subdia]['RendLiqDia'])
                self._cMensal.update({dia:{'RendBrMes':RendBrutoMensal, 
                                           'IrMes':IrMensal, 
                                           'RendLiqMes':RendLiqMensal}})

    def _RelatorioDiario(self):
        self.__Calc_RendDia()
        mask = "{0}, {1:0.8f}, {2:0.2f}, {3:0.2f}, {4:0.2f}, {5:0.2f}, {6:0.2f}"
        for dia in self.Dias(Opt=3):
            if dia in self._cDiario.keys():
                print(mask.format(dia, self._cDiario[dia]['TaxDia'],
                                  self._cDiario[dia]['RendBrDia'],
                                  self._cDiario[dia]['IrDia'],
                                  self._cDiario[dia]['RendLiqDia'],
                                  self._cDiario[dia]['SDBrutoDia'],
                                  self._cDiario[dia]['SDLiqDia']))

    def _RelatorioMensal(self):
        self.__Calc_RendMensal()
        mask = "{0}, {1:0.2f}, {2:0.2f}, {3:0.2f}"
        for dia in self.Dias(Opt=3):
            if dia in self._cMensal.keys():
                print(mask.format(dia, self._cMensal[dia]['RendBrMes'],
                                  self._cMensal[dia]['IrMes'],
                                  self._cMensal[dia]['RendLiqMes']))
      
#================== Fim Classe RendaFixa ========================================================


#================== Inicio Classe CDB ========================================================
class CDB(RendaFixa):
    '''
        Classe base para a criação de um CDB (Certificado de Depósito Bancário)

        Parâmetros
        ----------
            CodAplic - (OBRIGATORIO) - uma string que representa um nome para identificação do CDB

            ValorAplicado - (OBRIGATORIO) - o valor do investimento em CDB que se quer calcular

            ContratoCDI - (OPICIONAL) - o percentual do CDI pelo qual o CDB foi contratado e que reflete
                diretamente no cálculo do rendimento bruto. O valor padrão é igual a 100, ou 100% do CDI.

            Path_CDI - (OPICIONAL) - o path completo para o arquivo no formato pickle que contém o CDI
                diário obtido do site do Banco Central do Brasil.

            Data_Inicio - (OBRIGATORIA) - string que representa uma data no formato "xx/xx/xxxx"; a data
                inicial do investimento ou aplicação em CDB.

            Data_Fim - (OBRIGATORIA) - string que representa uma data no formato "xx/xx/xxxx"; é a data final
                ou de vencimento do investimento ou aplicação em CDB.

            Path_Arquivo - (OBRIGATORIA) - string representando o caminho (path) para o arquivo tipo csv contendo os feriados nacionais, 
                no formato (c:\\foo)

            Exemplos
            --------
                1) Criando um CDB com as seguintes características:
                    Nome = 130911Sant
                    Valor Aplicado = 1000000,00
                    ContratoCDI = 103,10% do CDI diário
                    Data de Inicio = 14/09/2011
                    Data de Vencimento = 31/07/2013
                    Arquivo contendo CDI diário = 'C:\\Apostilas\\Python\\BCB\\ProjFinanPy\\CDICetip.pkl'
                    Arquivo contendo lista de feriados nacionais = 'C:\\Apostilas\\Python\\BCB\\feriados_nacionais.csv'


                    arqferiados = 'C:\\Apostilas\\Python\\BCB\\feriados_nacionais.csv'
                    arqCDI = 'C:\\Apostilas\\Python\\BCB\\ProjFinanPy\\CDICetip.pkl'

                    cdb1 = CDBClasse.CDB('130911Sant', 1000000.00, 103.1, arqCDI, '14/09/2011', '31/07/2013',
                        Path_Arquivo = arqferiados)

                2) Obtendo um relatório resumo contendo o Rendimento Bruto, Imposto de Renda e Rendimento Liquido 
                    acumulados mensalmente, desde o inicio do investimento:

                        print(cdb1._RelatorioMensal())

    '''
    def __init__(self, CodAplic, ValorAplicado, ContratoCDI=100, Path_CDI='', Data_Inicio=None,
            Data_Fim=None, NumDias=1, Opt=1, Path_Arquivo=''):
                self._cCodAplic = CodAplic
                self._cValorAplicado = ValorAplicado
                self._cContratoCDI = ContratoCDI
                self._cPath_CDI = Path_CDI
                self._cData_Inicio = Data_Inicio
                self._cData_Fim = Data_Fim
                self._cNumDias = NumDias
                self._cOpt = Opt
                self._cPath_Arquivo = Path_Arquivo
                RendaFixa.__init__(self, self._cValorAplicado, self._cContratoCDI, self._cPath_CDI, self._cData_Inicio,
                    self._cData_Fim, self._cNumDias,  self._cOpt, self._cPath_Arquivo)
#================== Fim Classe CDB ========================================================


def main():
    pass

if __name__ == '__main__':
    main()







