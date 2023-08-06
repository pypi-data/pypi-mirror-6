#This file is part of seurvalencia. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from seurvalencia.api import API

from xml.dom.minidom import parseString
import os
import base64
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class Picking(API):
    """
    Picking API
    """
    __slots__ = ()

    def create(self, data):
        """
        Create a picking using the given data

        :param data: Dictionary of values
        :return: reference (str), label (pdf), error (str)
        """
        reference = None
        label = None
        error = None

        tmpl = loader.load('picking_send.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'adn_aduana_destino': data.get('adn_aduana_destino', ''),
            'adn_aduana_origen': data.get('adn_aduana_origen', ''),
            'adn_tipo_mercancia': data.get('adn_tipo_mercancia', ''),
            'adn_valor_declarado': data.get('adn_valor_declarado', '0'),
            'b2c_canal_preaviso1': data.get('b2c_canal_preaviso1', 'N'),
            'b2c_canal_preaviso2': data.get('b2c_canal_preaviso2', 'N'),
            'b2c_canal_preaviso3': data.get('b2c_canal_preaviso3', 'N'),
            'b2c_canal1': data.get('b2c_canal1', ''),
            'b2c_canal2': data.get('b2c_canal2', ''),
            'b2c_canal3': data.get('b2c_canal3', ''),
            'b2c_fecha_entrega': data.get('b2c_fecha_entrega', ''),
            'b2c_test_llegada': data.get('b2c_test_llegada', ''),
            'b2c_test_preaviso': data.get('b2c_test_preaviso', 'N'),
            'b2c_test_reparto': data.get('b2c_test_reparto', 'N'),
            'b2c_turno_reparto': data.get('b2c_turno_reparto', ''),
            'blt_observaciones': data.get('blt_observaciones', ''),
            'blt_referencia': data.get('blt_referencia', ''),
            'cab_producto': data.get('cab_producto', '2'),
            'cab_servicio': data.get('cab_servicio', '1'),
            'csg_atencion_de': data.get('csg_atencion_de', ''),
            'csg_ccc': data.get('csg_ccc', ''),
            'csg_codigo_postal': data.get('csg_codigo_postal', ''),
            'csg_escalera': data.get('csg_escalera', '.'),
            'csg_nombre': data.get('csg_nombre', ''),
            'csg_nombre_via': data.get('csg_nombre_via', ''),
            'csg_numero_via': data.get('csg_numero_via', '.'),
            'csg_pais': data.get('csg_pais', 'ES'),
            'csg_piso': data.get('csg_piso', '.'),
            'csg_poblacion': data.get('csg_poblacion', ''),
            'csg_puerta': data.get('csg_puerta', '.'),
            'csg_telefono': data.get('csg_telefono', ''),
            'csg_tipo_numero_via': data.get('csg_tipo_numero_via', 'N'),
            'csg_tipo_via': data.get('csg_tipo_via', 'CL'),
            'exp_bultos': data.get('exp_bultos', '1'),
            'exp_cambio': data.get('exp_cambio', ''),
            'exp_cde': data.get('exp_cde', ''),
            'exp_portes': data.get('exp_portes', ''),  # F: Facturacion
            'exp_reembolso': data.get('exp_reembolso', ''),  # F: Facturacion
            'exp_seguro': data.get('exp_seguro', ''),
            'exp_entregar_sabado': data.get('exp_entregar_sabado', ''),
            'exp_lc': data.get('exp_lc', ''),
            'exp_observaciones': data.get('exp_observaciones', ''),
            'exp_peso': data.get('exp_peso', '0.1'),
            'exp_referencia': data.get('exp_referencia', ''),
            'exp_valor_reembolso': data.get('exp_valor_reembolso', ''),
            'exp_valor_seguro': data.get('exp_valor_seguro', '0'),
            'fr_centro_logistico': data.get('fr_centro_logistico', ''),
            'fr_almacenar_hasta': data.get('fr_almacenar_hasta', ''),
            'fr_tipo_embalaje': data.get('fr_tipo_embalaje', ''),
            'fr_almacenar_hasta': data.get('fr_almacenar_hasta', ''),
            'fr_entrega_sabado': data.get('fr_entrega_sabado', ''),
            'fr_embalaje': data.get('fr_embalaje', ''),
            'fr_etiqueta_control': data.get('fr_etiqueta_control', ''),
            'gs_codigo': data.get('gs_codigo', '0'),
            'gs_codigo_centro': data.get('gs_codigo_centro', ''),
            'gs_codigo_departamento': data.get('gs_codigo_departamento', ''),
            'gs_consolidar_pedido': data.get('gs_consolidar_pedido', ''),
            'gs_fecha_entrega': data.get('gs_fecha_entrega', ''),
            'gs_hora_desde': data.get('gs_hora_desde', ''),
            'gs_hora_hasta': data.get('gs_hora_hasta', ''),
            'gs_numero_pedido': data.get('gs_numero_pedido', ''),
            'gs_consignatario': data.get('gs_consignatario', ''),
            'gs_tipo_mercancia': data.get('gs_tipo_mercancia', ''),
            'int_divisa': data.get('int_divisa', ''),
            'int_famimila_mercancia': data.get('int_famimila_mercancia', ''),
            'int_producto_mercancia': data.get('int_producto_mercancia', ''),
            'int_codigo_pais': data.get('int_codigo_pais', ''),
            'int_codigo_postal': data.get('int_codigo_postal', ''),
            'int_contracto': data.get('int_contracto', ''),
            'int_extension_direccion': data.get('int_extension_direccion', ''),
            'int_telefono': data.get('int_telefono', '0'),
            'int_courier': data.get('int_courier', '0'),
            'int_mercancia': data.get('int_mercancia', '0'),
            'int_codigo_pais': data.get('int_codigo_pais', ''),
            'int_codigo_postal': data.get('int_codigo_postal', ''),
            'int_valor_declarado': data.get('int_valor_declarado', '0'),
            }
        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        dom = parseString(result)

        #Get message error from XML
        mensaje = dom.getElementsByTagName('mensaje')
        if mensaje:
            if mensaje[0].firstChild.data == 'ERROR':
                error = 'Seur return an error when send shipment %s' % vals.get('ref_bulto')
                return reference, label, error

        #Get reference from XML
        ecb = dom.getElementsByTagName('ECB')
        if ecb:
            reference = ecb[0].childNodes[0].firstChild.data

        #Get Label file from XML
        document = dom.getElementsByTagName('DocumentoImpresion')
        if document:
            label = document[0].firstChild.data

        return reference, label, error

    def info(self):
        """
        Get today deliveries (shipments) in PDF from Seur Valencia

        :return: PDF file
        """
        tmpl = loader.load('picking_info.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            }

        url = 'https://ws.seur.com/webseur/services/WSConsultaExpediciones'
        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        dom = parseString(result)

        #Get info
        info = dom.getElementsByTagName('out')

        response = dom.getElementsByTagName('wsImprimirManifiestoPDFResult')
        info = response[0].firstChild.data
        return base64.b64decode(info)
