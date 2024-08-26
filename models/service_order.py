from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServiceOrder(models.Model):
    _name = 'service.order'
    _description = 'Orden de Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Número de Orden', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    quotation_id = fields.Many2one('service.quotation', string='Cotización Relacionada')
    service_type = fields.Selection([
        ('repair', 'Reparación'),
        ('installation', 'Instalación'),
        ('maintenance', 'Mantenimiento'),
    ], string='Tipo de Servicio', required=True)
    description = fields.Text('Descripción del Servicio')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirmed', 'Confirmada'),
        ('material_ready', 'Materiales Listos'),
        ('scheduled', 'Programada'),
        ('in_progress', 'En Proceso'),
        ('done', 'Finalizada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', tracking=True)
    technician_id = fields.Many2one('hr.employee', string='Técnico Asignado')
    scheduled_date = fields.Datetime('Fecha Programada')
    completion_date = fields.Datetime('Fecha de Finalización')
    visit_ids = fields.One2many('service.visit', 'service_order_id', string='Visitas')
    material_ids = fields.One2many('service.order.material', 'service_order_id', string='Materiales')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('service.order') or _('New')
        return super(ServiceOrder, self).create(vals)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_materials_ready(self):
        self.write({'state': 'material_ready'})

    def action_schedule(self):
        return {
            'name': _('Programar Visita'),
            'type': 'ir.actions.act_window',
            'res_model': 'service.schedule.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_service_order_id': self.id},
        }

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done', 'completion_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

class ServiceOrderMaterial(models.Model):
    _name = 'service.order.material'
    _description = 'Materiales de Orden de Servicio'

    service_order_id = fields.Many2one('service.order', string='Orden de Servicio', required=True)
    product_id = fields.Many2one('product.product', string='Producto', required=True)
    quantity = fields.Float('Cantidad', default=1.0)
    is_available = fields.Boolean('Disponible', default=False)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.is_available = self.product_id.qty_available > 0