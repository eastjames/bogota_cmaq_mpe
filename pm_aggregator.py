'''
def ob_row_col():
    # obcol and obrow are 14 observation site locations
    obcol = [ 32, 36, 28, 38, 29, 40, 27, 36, 37, 32, 36, 35, 30, 42 ]	
    obrow = [ 44, 34, 27, 33, 36, 48, 30, 38, 31, 31, 25, 46, 25, 40 ]
    return obrow, obcol
'''

def get_spcs():
    '''
    Returns list of species used to aggregate PM25
    from the ACONC file and AERODIAM file
    '''
    #obspcs = ['CO','NOx','O3','SO2','PM25','PM10'] # TEMP2 not in monet obj
#    obspcs = ['PM25'] # TEMP2 not in monet obj
    #modspcs = ['CO','NOx','O3','SO2','PM25','PM10'] # TEMP2 not in monet obj

    PMI_TOT = 'ASO4I + ANH4I + ANO3I + APOCI + APNCOMI + AECI + AH2OI + ACLI'
    PMJ_TOT = 'ASO4J + ANH4J + ANO3J + AALKJ + AXYL1J + AXYL2J + AXYL3J + ATOL1J + \
               ATOL2J + ATOL3J + ABNZ1J + ABNZ2J + ABNZ3J + ATRP1J + ATRP2J + \
               AISO1J + AISO2J + ASQTJ + AORGCJ + APOCJ + APNCOMJ + AECJ + AOTHRJ + \
               AFEJ + AALJ + ASIJ + ATIJ + ACAJ + AMGJ + AKJ + AMNJ + AH2OJ + \
               ANAJ + ACLJ + AISO3J + AOLGAJ + AOLGBJ'
    PMK_TOT = 'ACLK + ASO4K + ANH4K + ANO3K + AH2OK + ACORS + ASOIL + ASEACAT'
    PM      = 'ANAI + AOTHRI' 
 
    PMI_TOT = [pmi.strip() for pmi in PMI_TOT.split(' + ')] 
    PMJ_TOT = [pmj.strip() for pmj in PMJ_TOT.split(' + ')] 
    PMK_TOT = [pmk.strip() for pmk in PMK_TOT.split(' + ')] 
    PM      = [pm.strip()  for pm  in PM.split(' + ')]    

    modspcs = PMI_TOT + PMJ_TOT + PMK_TOT + PM
    return modspcs

def pm_total( modx, adx ):
    '''
    Returns total PM2.5 and PM10 based on CMAQ output
    Return is xarray data array
    Requires ACONC file and AERODIAM file
    '''
    AOMIJ      =  modx['AXYL1J']+modx['AXYL2J']+modx['AXYL3J']+modx['ATOL1J']+modx['ATOL2J']+\
                  modx['ATOL3J']+modx['ABNZ1J']+modx['ABNZ2J']+modx['ABNZ3J']+modx['AISO1J']+\
                  modx['AISO2J']+modx['AISO3J']+modx['ATRP1J']+modx['ATRP2J']+modx['ASQTJ']+\
                  modx['AALKJ']+modx['AORGCJ']+modx['AOLGBJ']+modx['AOLGAJ']+modx['APOCI']+\
                  modx['APOCJ']+modx['APNCOMI']+modx['APNCOMJ']
    ATOTI      =  modx['ASO4I']+modx['ANO3I']+modx['ANH4I']+modx['ANAI']+modx['ACLI']+\
                  modx['AECI']+modx['APOCI']+modx['APNCOMI']+modx['AOTHRI']
    ATOTJ      =  modx['ASO4J']+modx['ANO3J']+modx['ANH4J']+modx['ANAJ']+modx['ACLJ']+\
                  modx['AECJ']+AOMIJ-(modx['APOCI']+modx['APNCOMI'])+modx['AOTHRJ']+\
                  modx['AFEJ']+modx['ASIJ']+modx['ATIJ']+modx['ACAJ']+modx['AMGJ']+\
                  modx['AMNJ']+modx['AALJ']+modx['AKJ']
    ATOTK      =  modx['ASOIL']+modx['ACORS']+modx['ASEACAT']+modx['ACLK']+modx['ASO4K']+\
                  modx['ANO3K']+modx['ANH4K']
    PMIJ       =  ATOTI+ATOTJ
    PM10       =  PMIJ+ATOTK
    PM25_TOT   =  ATOTI*adx['PM25AT']+ATOTJ*adx['PM25AC']+ATOTK*adx['PM25CO']

    return PM25_TOT, PM10


def pm_total2( modx, adx ):
    '''
    To match UFL definition
    Returns total PM2.5 and PM10 based on CMAQ output
    Return is xarray data array
    Requires ACONC file and AERODIAM file
    '''
    PMI_TOT = modx['ASO4I'] + modx['ANH4I'] + modx['ANO3I'] + modx['APOCI'] +\
              modx['APNCOMI'] + modx['AECI'] + modx['AH2OI'] +  modx['ACLI']
    PMJ_TOT = modx['ASO4J'] + modx['ANH4J'] + modx['ANO3J'] + modx['AALKJ'] +\
              modx['AXYL1J'] + modx['AXYL2J'] +modx['AXYL3J'] + modx['ATOL1J'] +\
              modx['ATOL2J'] + modx['ATOL3J'] + modx['ABNZ1J'] + modx['ABNZ2J'] +\
              modx['ABNZ3J'] + modx['ATRP1J'] + modx['ATRP2J'] + modx['AISO1J'] +\
              modx['AISO2J'] + modx['ASQTJ'] + modx['AORGCJ'] + modx['APOCJ'] +\
              modx['APNCOMJ'] + modx['AECJ'] + modx['AOTHRJ'] + modx['AFEJ'] +\
              modx['AALJ'] + modx['ASIJ'] + modx['ATIJ'] + modx['ACAJ'] +\
              modx['AMGJ'] + modx['AKJ'] + modx['AMNJ'] + modx['AH2OJ'] +\
              modx['ANAJ'] + modx['ACLJ'] + modx['AISO3J'] + modx['AOLGAJ']+\
              modx['AOLGBJ']
    PMK_TOT = modx['ACLK'] + modx['ASO4K'] + modx['ANH4K'] + modx['ANO3K'] +\
              modx['AH2OK'] + modx['ACORS'] + modx['ASOIL'] + modx['ASEACAT']
    PM25_TOT = PMI_TOT*adx['PM25AT'] + PMJ_TOT*adx['PM25AC'] + PMK_TOT*adx['PM25CO']
    PM10 = PMI_TOT + PMJ_TOT + PMK_TOT

    return PM25_TOT, PM10


def pm_species( modx, adx ):
    '''
    returns PM25_NH4, PM25_NO3, PM25_SO4
    '''

    # crustal elements
    AFEJ = modx['AFEJ']
    AALJ = modx['AALJ']
    ASIJ = modx['ASIJ']
    ATIJ = modx['ATIJ']
    ACAJ = modx['ACAJ']
    AMGJ = modx['AMGJ']
    AKJ = modx['AKJ']
    AMNJ = modx['AMNJ']
    #ASOILJ = 2.20*AALJ+2.49*ASIJ+1.63*ACAJ+2.42*AFEJ+1.94*ATIJ
    ASOILJ = AALJ+ASIJ+ACAJ+AFEJ+ATIJ
    # other PM species
    ANAK       =  0.8373*modx['ASEACAT']+0.0626*modx['ASOIL']+0.0023*modx['ACORS']
    AMGK       =  0.0997*modx['ASEACAT']                +0.0032*modx['ACORS']
    AKK        =  0.0310*modx['ASEACAT']+0.0242*modx['ASOIL']+0.0176*modx['ACORS']
    ACAK       =  0.0320*modx['ASEACAT']+0.0838*modx['ASOIL']+0.0562*modx['ACORS']
    ACLIJ      =  modx['ACLI']+modx['ACLJ']
    AECIJ      =  modx['AECI']+modx['AECJ']
    ANAIJ      =  modx['ANAJ']+modx['ANAI']
    ANO3IJ     =  modx['ANO3I']+modx['ANO3J']
    ANO3K      =  modx['ANO3K']
    ANH4IJ     =  modx['ANH4I']+modx['ANH4J']
    ANH4K      =  modx['ANH4K']
    AOCIJ      = (modx['AXYL1J']+modx['AXYL2J']+modx['AXYL3J'])/2.0+(modx['ATOL1J']+\
                  modx['ATOL2J']+modx['ATOL3J'])/2.0+(modx['ABNZ1J']+modx['ABNZ2J']+\
                  modx['ABNZ3J'])/2.0 +(modx['AISO1J']+modx['AISO2J'])/1.6+modx['AISO3J']/2.7+\
                 (modx['ATRP1J']+modx['ATRP2J'])/1.4+modx['ASQTJ']/2.1+0.64*modx['AALKJ']+\
                  modx['AORGCJ']/2.0+(modx['AOLGBJ']+modx['AOLGAJ'])/2.1+modx['APOCI']+modx['APOCJ']
    AOMIJ      =  modx['AXYL1J']+modx['AXYL2J']+modx['AXYL3J']+modx['ATOL1J']+modx['ATOL2J']+\
                  modx['ATOL3J']+modx['ABNZ1J']+modx['ABNZ2J']+modx['ABNZ3J']+modx['AISO1J']+\
                  modx['AISO2J']+modx['AISO3J']+modx['ATRP1J']+modx['ATRP2J']+modx['ASQTJ']+\
                  modx['AALKJ']+modx['AORGCJ']+modx['AOLGBJ']+modx['AOLGAJ']+modx['APOCI']+\
                  modx['APOCJ']+modx['APNCOMI']+modx['APNCOMJ']
    AORGAJ     =  modx['AXYL1J']+modx['AXYL2J']+modx['AXYL3J']+modx['ATOL1J']+modx['ATOL2J']+\
                  modx['ATOL3J']+modx['ABNZ1J']+modx['ABNZ2J']+modx['ABNZ3J']+modx['AALKJ']+\
                  modx['AOLGAJ']
    AORGBJ     =  modx['AISO1J']+modx['AISO2J']+modx['AISO3J']+modx['ATRP1J']+modx['ATRP2J']+\
                  modx['ASQTJ']+modx['AOLGBJ']
    AORGCJ     =  modx['AORGCJ']
    APOCIJ     =  modx['APOCI']+modx['APOCJ']
    APOAIJ     =  APOCIJ+modx['APNCOMI']+modx['APNCOMJ']
    ASO4IJ     =  modx['ASO4I']+modx['ASO4J']
    ASO4K      =  modx['ASO4K']
    ATOTI      =  modx['ASO4I']+modx['ANO3I']+modx['ANH4I']+modx['ANAI']+modx['ACLI']+\
                  modx['AECI']+modx['APOCI']+modx['APNCOMI']+modx['AOTHRI']
    ATOTJ      =  modx['ASO4J']+modx['ANO3J']+modx['ANH4J']+modx['ANAJ']+modx['ACLJ']+\
                  modx['AECJ']+AOMIJ-(modx['APOCI']+modx['APNCOMI'])+modx['AOTHRJ']+\
                  modx['AFEJ']+modx['ASIJ']+modx['ATIJ']+modx['ACAJ']+modx['AMGJ']+\
                  modx['AMNJ']+modx['AALJ']+modx['AKJ']
    ATOTK      =  modx['ASOIL']+modx['ACORS']+modx['ASEACAT']+modx['ACLK']+modx['ASO4K']+\
                  modx['ANO3K']+modx['ANH4K']
    PMIJ       =  ATOTI+ATOTJ
    PM10       =  PMIJ+ATOTK
    AUNSPEC1IJ =  PMIJ - (ASOILJ + ANO3IJ + ASO4IJ + ANH4IJ + AOCIJ + AECIJ + ANAIJ + ACLIJ)
    ANCOMIJ    =  AOMIJ-AOCIJ
    AUNSPEC2IJ =  AUNSPEC1IJ - ANCOMIJ
#     OM/OC ratios
    AOMOCRAT_PRI     =      APOAIJ/APOCIJ
    AOMOCRAT_TOT     =      AOMIJ/AOCIJ
#     PM25 
    PM25_CL    =  modx['ACLI']*adx['PM25AT']+modx['ACLJ']*adx['PM25AC']+modx['ACLK']*adx['PM25CO']
    PM25_EC    =  modx['AECI']*adx['PM25AT']+modx['AECJ']*adx['PM25AC']
    PM25_NA    =  modx['ANAI']*adx['PM25AT']+modx['ANAJ']*adx['PM25AC']+ANAK*adx['PM25CO']
    PM25_MG    =                             modx['AMGJ']*adx['PM25AC']+AMGK*adx['PM25CO']
    PM25_K     =                             modx['AKJ'] *adx['PM25AC']+AKK *adx['PM25CO']
    PM25_CA    =                             modx['ACAJ']*adx['PM25AC']+ACAK*adx['PM25CO']
    PM25_NH4   =  modx['ANH4I']*adx['PM25AT']+modx['ANH4J']*adx['PM25AC']+modx['ANH4K']*adx['PM25CO']
    PM25_NO3   =  modx['ANO3I']*adx['PM25AT']+modx['ANO3J']*adx['PM25AC']+modx['ANO3K']*adx['PM25CO']
    PM25_OC    =  modx['APOCI']*adx['PM25AT']+(AOCIJ-modx['APOCI'])*adx['PM25AC']
    PM25_SOIL  =  ASOILJ*adx['PM25AC']+(modx['ASOIL']+modx['ACORS'])*adx['PM25CO']
    PM25_SO4   =  modx['ASO4I']*adx['PM25AT']+modx['ASO4J']*adx['PM25AC']+modx['ASO4K']*adx['PM25CO']
    PM25_TOT   =  ATOTI*adx['PM25AT']+ATOTJ*adx['PM25AC']+ATOTK*adx['PM25CO']
    PM25_UNSPEC1 =   PM25_TOT-(PM25_CL + PM25_EC + PM25_NA + PM25_NH4 + PM25_NO3 +\
                               PM25_OC + PM25_SOIL + PM25_SO4)
    PMC_CL     =  modx['ACLI']+modx['ACLJ']+modx['ACLK']-PM25_CL
    PMC_NA     =  modx['ANAI']+modx['ANAK']*0.78 - PM25_NA
    PMC_NH4    =  modx['ANH4I']+modx['ANH4J']+modx['ANH4K']-PM25_NH4
    PMC_NO3    =  modx['ANO3I']+modx['ANO3J']+modx['ANO3K']-PM25_NO3
    PMC_SO4    =  modx['ASO4I']+modx['ASO4J']+modx['ASO4K']-PM25_SO4
    PMC_TOT    =  PM10-PM25_TOT
    
    CRUSTAL = (modx['ACAJ']+modx['AMGJ']+modx['AKJ']+modx['AMNJ'])*adx['PM25AC']
    OM = ((modx['AXYL1J']+modx['AXYL2J']+modx['AXYL3J']+modx['ATOL1J']+modx['ATOL2J']+\
                  modx['ATOL3J']+modx['ABNZ1J']+modx['ABNZ2J']+modx['ABNZ3J'])*0.5+(modx['AISO1J']+\
                  modx['AISO2J'])*0.375+modx['AISO3J']*(1.-1./2.7)+(modx['ATRP1J']+\
                  modx['ATRP2J'])*(1.-1./1.4)+modx['ASQTJ']*(1.-1./2.1)+modx['AALKJ']*0.36+\
                  modx['AORGCJ']*0.5+(modx['AOLGBJ']+modx['AOLGAJ'])*(1.-1./2.1))*adx['PM25AC'] 
    NCOM = modx['APNCOMJ']*adx['PM25AC']+modx['APNCOMI']*adx['PM25AT']
    AOTHR = modx['AOTHRJ']*adx['PM25AC']+modx['AOTHRI']*adx['PM25AT']
    SEA = modx['ASEACAT']*adx['PM25CO']
    PM25UNSP = OM+NCOM+AOTHR+CRUSTAL+SEA

    return PM25_NH4, PM25_NO3, PM25_SO4

def pm25_nh4( modx, adx ):
    PM25_NH4   =  modx['ANH4I']*adx['PM25AT']+modx['ANH4J']*adx['PM25AC']+modx['ANH4K']*adx['PM25CO']
    return PM25_NH4

def pm25_no3( modx, adx ):
    PM25_NO3   =  modx['ANO3I']*adx['PM25AT']+modx['ANO3J']*adx['PM25AC']+modx['ANO3K']*adx['PM25CO']
    return PM25_NO3

def pm25_so4( modx, adx ):
    PM25_SO4   =  modx['ASO4I']*adx['PM25AT']+modx['ASO4J']*adx['PM25AC']+modx['ASO4K']*adx['PM25CO']
    return PM25_SO4


