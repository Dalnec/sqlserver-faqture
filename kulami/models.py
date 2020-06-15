import pyodbc
import decimal
from base.db import __conectarse

class Venta:
    tipo_venta = None
    serie_documento = None
    numero_documento = None
    fecha_venta = None
    nombre_cliente = None
    numero_documento_cliente = None
    direccion_cliente = None
    codigo_cliente = None
    vendedor = None
    total_venta = None
    codigo_tipo_documento = None
    id_venta = None
    codigo_tipo_documento_identidad = None
    telefono = None
    total_descuentos = None
    detalle_ventas = []

    def __str__(self):
        return "{} - {} {}".format(self.tipo_venta, self.serie_documento, self.detalle_ventas)


class DetalleVenta:
    def __init__(self, codigo_producto, nombre_producto, cantidad, precio_producto, unidad_medida):
        self.codigo_producto = codigo_producto
        self.nombre_producto = nombre_producto
        self.cantidad = int(cantidad)
        self.precio_producto = float(precio_producto)
        self.unidad_medida = unidad_medida

    def __str__(self):
        return self.nombre_producto

def leer_db_access():
    cnx = __conectarse()
    cursor = cnx.cursor()
    lista_ventas = []
    
    sql_header = """
            SELECT 
                [IdVen]
                ,SUBSTRING(V.NroVen, 0, 4) AS serie_documento 
                ,SUBSTRING(V.NroVen, 5, 7) AS numero_documento
                ,V.[FecVen]
                ,V.[UsuPer]  
                ,V.[SubTot]
                ,V.[IgvTot]
                ,V.[EfeVen]
                ,V.[IdCli]
                ,V.[TipDoc]
                ,C.RucCli AS numero_doc
                ,V.[RazCli]   
                ,C.DirCli AS direccion
                ,C.TelCli AS telefono
                ,V.[Obs]
                ,V.[CorVen]
            FROM [Labbio].[dbo].[TBLVentas] AS V,
                    [Labbio].[dbo].[TBLCliente] AS C            
            WHERE V.IdCli = C.IdCli
                    AND V.FecVen >= '2020-05-22'
                    AND V.TipDoc IN ('BOLETA','FACTURA')
					AND V.Obs != 'PROCESADO'
            ORDER BY V.IdVen
        """
    sql_detail = """
            SELECT       
                TBLDetaVentas.IdExa AS codigo_interno, 
                TBLExamen.NomExa AS descripcion,
                TBLDetaVentas.CanExa, 
                TBLDetaVentas.PreExa, 
                TBLDetaVentas.EfeVen
            FROM            
                [Labbio].[dbo].[TBLDetaVentas] INNER JOIN
                [Labbio].[dbo].[TBLExamen] ON TBLDetaVentas.IdExa = TBLExamen.IdExa
            WHERE        
                (TBLDetaVentas.IdVen = {}) 
        """
    cursor.execute(sql_header)

    for row in cursor.fetchall():
        venta = Venta()
        venta.id_venta = row[0]
        venta.serie_documento = row[1]
        venta.numero_documento = row[2]
        venta.fecha_venta = row[3]        
        venta.vendedor = row[4]        
        venta.total_venta = row[7]
        venta.codigo_cliente = row[8]        
        venta.codigo_tipo_documento = row[9]
        venta.numero_documento_cliente = row[10]       
        venta.nombre_cliente = row[11]        
        venta.direccion_cliente = row[12] if row[12] != None else ''
        venta.telefono = row[13]        
        venta.total_bolsa_plastica = 0
        venta.total_descuentos = row[15]
        
        detalle_ventas = []
        cursor.execute(sql_detail.format(venta.id_venta))
        for deta in cursor.fetchall():
            detalle_ventas.append(DetalleVenta(deta[0], deta[1], deta[2], deta[3], "UND"))

        venta.detalle_ventas = detalle_ventas
        lista_ventas.append(venta)

    cursor.close()
    cnx.close()
    return _generate_lista(lista_ventas)

def _generate_lista(ventas):
    
    header_dics = []
    for venta in ventas:
        codigo_tipo_operacion = '0101'
        codigo_tipo_moneda = 'PEN'
        header_dic = {}

        if venta.codigo_tipo_documento == 'BOLETA':
            serie_documento = "B" + venta.serie_documento
            codigo_tipo_documento = '03'
            codigo_tipo_documento_identidad = 1
        else:
            serie_documento = "F" + venta.serie_documento
            codigo_tipo_documento = '01'
            codigo_tipo_documento_identidad = 6
        
        # opcionales
        header_dic['id_venta'] = int(venta.id_venta)
        
        # Creamos el cuerpo del pse
        header_dic['serie_documento'] = serie_documento
        header_dic['numero_documento'] = int(venta.numero_documento)
        header_dic['fecha_de_emision'] = venta.fecha_venta.strftime('%Y-%m-%d')
        header_dic['hora_de_emision'] = venta.fecha_venta.strftime('%H:%M:%S')
        header_dic['codigo_tipo_operacion'] = codigo_tipo_operacion
        header_dic['codigo_tipo_documento'] = codigo_tipo_documento
        header_dic['codigo_tipo_moneda'] = codigo_tipo_moneda
        header_dic['fecha_de_vencimiento'] = venta.fecha_venta.strftime(
            '%Y-%m-%d')
        header_dic['numero_orden_de_compra'] = ''

        # totales
        datos_totales = {}
        datos_totales['total_descuentos'] = round(float(venta.total_descuentos), 2)
        datos_totales['total_exportacion'] = 0
        datos_totales['total_operaciones_gravadas'] = 0
        datos_totales['total_operaciones_inafectas'] = 0
        datos_totales['total_operaciones_exoneradas'] = round(float(venta.total_venta), 2)
        datos_totales['total_operaciones_gratuitas'] = 0
        #datos_totales['total_impuesto_bolsa_plastica'] = venta.total_bolsa_plastica
        datos_totales['total_igv'] = 0
        datos_totales['total_impuestos'] = 0
        datos_totales['total_valor'] = round(float(venta.total_venta), 2)
        datos_totales['total_venta'] = round(float(venta.total_venta), 2)

        header_dic['totales'] = datos_totales

        # datos del cliente
        datos_del_cliente = {}
        datos_del_cliente['codigo_tipo_documento_identidad'] = codigo_tipo_documento_identidad
        datos_del_cliente['numero_documento'] = venta.numero_documento_cliente
        datos_del_cliente['apellidos_y_nombres_o_razon_social'] = venta.nombre_cliente
        datos_del_cliente['codigo_pais'] = 'PE'
        datos_del_cliente['ubigeo'] = ''
        datos_del_cliente['direccion'] = venta.direccion_cliente
        datos_del_cliente['correo_electronico'] = ''
        datos_del_cliente['telefono'] = ''

        header_dic['datos_del_cliente_o_receptor'] = datos_del_cliente
        
        lista_items = []
        for deta in venta.detalle_ventas:
            item = {}
            item['codigo_interno'] = deta.codigo_producto
            item['descripcion'] = deta.nombre_producto
            item['codigo_producto_sunat'] = ''
            item['unidad_de_medida'] = 'NIU'
            item['cantidad'] = deta.cantidad
            item["valor_unitario"] = deta.precio_producto
            item['codigo_tipo_precio'] = '01'
            item['precio_unitario'] = deta.precio_producto
            item['codigo_tipo_afectacion_igv'] = '20'
            item['total_base_igv'] = 0
            item['porcentaje_igv'] = 18
            item['total_igv'] = 0
            #item['total_impuestos_bolsa_plastica'] = 0
            item['total_impuestos'] = 0
            item['total_valor_item'] = (deta.cantidad * deta.precio_producto)
            item['total_item'] = (deta.cantidad * deta.precio_producto)
            #item['posicion'] = deta.posicion
            lista_items.append(item)

        header_dic['items'] = lista_items
        header_dics.append(header_dic)
    return header_dics