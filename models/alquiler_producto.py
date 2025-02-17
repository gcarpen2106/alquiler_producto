# models/alquiler_producto.py

from odoo import models, fields, api
from datetime import datetime, timedelta

class AlquilerProducto(models.Model):
    _name = 'alquiler.producto'
    _description = 'Gestión de Alquiler de Productos'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='Nuevo')
    cliente_id = fields.Many2one('res.partner', string='Cliente', required=True)
    producto_id = fields.Many2one('product.product', string='Producto', required=True)
    fecha_inicio = fields.Date(string='Fecha de Inicio', required=True, default=fields.Date.today)
    fecha_fin = fields.Date(string='Fecha de Fin', compute='_compute_fecha_fin', store=True)
    observaciones = fields.Text(string='Observaciones')

    state = fields.Selection([
        ('en_alquiler', 'En Alquiler'),
        ('entregado', 'Entregado'),
        ('no_entregado', 'No Entregado')
    ], string='Estado', default='en_alquiler', tracking=True)
    
    producto_disponible = fields.Boolean(string='Producto Disponible', compute='_compute_producto_disponible')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('alquiler.producto') or 'Nuevo'
        return super(AlquilerProducto, self).create(vals)

    @api.depends('fecha_inicio')
    def _compute_fecha_fin(self):
        for record in self:
            if record.fecha_inicio:
                record.fecha_fin = record.fecha_inicio + timedelta(days=30)

    @api.depends('producto_id')
    def _compute_producto_disponible(self):
        for record in self:
            if record.producto_id:
                cantidad_disponible = self.env['stock.quant'].search([
                    ('product_id', '=', record.producto_id.id),
                    ('location_id.usage', '=', 'internal')
                ]).mapped('quantity')
                record.producto_disponible = sum(cantidad_disponible) > 0
            else:
                record.producto_disponible = False

    @api.onchange('producto_id')
    def _onchange_producto_id(self):
        for record in self:
            if record.producto_id:
                # Verificar disponibilidad en el inventario
                cantidad_disponible = self.env['stock.quant'].search([
                    ('product_id', '=', record.producto_id.id),
                    ('location_id.usage', '=', 'internal')
                ]).mapped('quantity')
                record.producto_disponible = sum(cantidad_disponible) > 0
                
                if not record.producto_disponible:
                    return {
                        'warning': {
                            'title': 'Producto no disponible',
                            'message': 'El producto seleccionado se encuentra alquilado.'
                        }
                    }

    def check_alquileres_vencidos(self):
        alquileres_vencidos = self.search([
            ('state', '=', 'en_alquiler'),
            ('fecha_fin', '<', fields.Date.today())
        ])
        alquileres_vencidos.write({'state': 'no_entregado'})