#This file is part of seurvalencia. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

def seurvalencia_url(debug=False):
    """
    Seur URL connection

    :param debug: If set to true, use Seur test URL
    """
    if debug:
        return 'http://www.seurvalencia.es/IC/SERVICE.ASMX' #Not know url test
    else:
        return 'http://www.seurvalencia.es/IC/SERVICE.ASMX'

def services():
    services = {
        '001': 'SEUR - 24',
        '003': 'SEUR - 10',
        '005': 'MISMO DIA',
        '007': 'COURIER',
        '009': 'SEUR 13:30',
        '013': 'SEUR - 72',
        '015': 'S-48',
        '017': 'MARITIMO',
        '019': 'NETEXPRESS',
        '077': 'CLASSIC',
        '083': 'SEUR 8:30',
    }
    return services
