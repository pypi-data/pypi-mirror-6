#This file is part of seurvalencia. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from seurvalencia.utils import seurvalencia_url

from xml.dom.minidom import parseString
import urllib2
import os
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class API(object):
    """
    Generic API to connect to Seur Valencia
    """
    __slots__ = (
        'url',
        'username',
        'password',
    )

    def __init__(self, username, password, debug=False):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        Example usage ::

            from seurvalencia.api import API

            with API(username, password) as seurvalencia_api:
                return seurvalencia_api.test_connection()

        :param username: API username of the Seur Web Services.
        :param password: API password of the Seur Web Services.
        """
        self.url = seurvalencia_url(debug)
        self.username = username
        self.password = password

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

    def connect(self, xml):
        """
        Connect to the Webservices and return XML data from seurvalencia

        :param method: method service.
        :param xml: XML data.
        
        Return XML object
        """
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Host': 'seurvalencia.es',
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(xml),
            }
        request = urllib2.Request(self.url, xml, headers)
        try:
            response = urllib2.urlopen(request)
        except:
            return None
        return response.read()

    def test_connection(self):
        """
        Test connection to Seur webservices
        Send XML to Seur and return string
        """
        tmpl = loader.load('validate_user.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            }

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        if not result:
            return "Error 500 from Seur Valencia"
        dom = parseString(result)

        mensaje = dom.getElementsByTagName('wsValidarUsuarioResult')
        if mensaje:
            return mensaje[0].firstChild.data
        return "Not found wsValidarUsuarioResult attribute from Seur Valencia"

    def get_city(self, zipcode):
        """
        Get city data from a zip code
        Send XML to Seur and return dict
        """
        tmpl = loader.load('get_city.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'zip': zipcode,
            }

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        if not result:
            return "Error 500 from Seur Valencia"
        dom = parseString(result)

        registros = dom.getElementsByTagName('Registros')
        poblaciones = registros[0].getElementsByTagName('wsRegistroInfoPoblacionesCorto')
        values = []
        for poblacion in poblaciones:
            city = {}
            city['zip'] = poblacion.getElementsByTagName("CODIGO_POSTAL")[0].firstChild.data
            city['city_code'] = poblacion.getElementsByTagName("COD_POBLACION")[0].firstChild.data
            city['code_unidad'] = poblacion.getElementsByTagName("COD_UNIDAD_ADMIN")[0].firstChild.data
            city['city_name'] = poblacion.getElementsByTagName("NOM_POBLACION")[0].firstChild.data
            city['state_code'] = poblacion.getElementsByTagName("COD_PROVINCIA")[0].firstChild.data
            city['state_name'] = poblacion.getElementsByTagName("NOM_PROVINCIA")[0].firstChild.data
            city['clase_code'] = poblacion.getElementsByTagName("COD_CLASE_RECOG")[0].firstChild.data
            city['country_code'] = poblacion.getElementsByTagName("COD_PAIS_ISO")[0].firstChild.data
            city['ua'] = poblacion.getElementsByTagName("FIN_DES_R_ARRAS_UA")[0].firstChild.data
            city['ct'] = poblacion.getElementsByTagName("FIN_DES_R_ARRAS_CT")[0].firstChild.data
            values.append(city)
        return values
