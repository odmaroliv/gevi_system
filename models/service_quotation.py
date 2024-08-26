from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ServiceQuotation(models.Model):
    _name = 'service.quotation'
    _description = 'Cotización de Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Número de Cotización', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    date_quotation = fields.Date('Fecha de Cotización', default=fields.Date.context_today)
    validity_date = fields.Date('Válido Hasta')
    service_type = fields.Selection([
        ('repair', 'Reparación'),
        ('installation', 'Instalación'),
        ('maintenance', 'Mantenimiento'),
    ], string='Tipo de Servicio', required=True)
    description = fields.Text('Descripción del Servicio')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('sent', 'Enviada'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
        ('converted', 'Convertida'),
    ], string='Estado', default='draft', tracking=True)
    line_ids = fields.One2many('service.quotation.line', 'quotation_id', string='Líneas de Cotización')
    total_amount = fields.Float('Total', compute='_compute_total', store=True)
    service_order_id = fields.Many2one('service.order', string='Orden de Servicio', readonly=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('service.quotation') or _('New')
        return super(ServiceQuotation, self).create(vals)

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for quotation in self:
            quotation.total_amount = sum(line.subtotal for line in quotation.line_ids)

    def action_send_quotation(self):
        self.ensure_one()
        template = self.env.ref('advanced_service_management.email_template_service_quotation', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='service.quotation',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id if template else False,
            default_composition_mode='comment',
            mark_quotation_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_reject(self):
        self.write({'state': 'rejected'})

    def action_convert_to_order(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_("Solo se pueden convertir cotizaciones aprobadas."))
        
        order_vals = {
            'partner_id': self.partner_id.id,
            'quotation_id': self.id,
            'service_type': self.service_type,
            'description': self.description,
            'state': 'draft',
        }
        service_order = self.env['service.order'].create(order_vals)
        self.write({
            'state': 'converted',
            'service_order_id': service_order.id
        })
        return {
            'name': _('Orden de Servicio'),
            'view_mode': 'form',
            'res_model': 'service.order',
            'res_id': service_order.id,
            'type': 'ir.actions.act_window',
        }

class ServiceQuotationLine(models.Model):
    _name = 'service.quotation.line'
    _description = 'Línea de Cotización de Servicio'

    quotation_id = fields.Many2one('service.quotation', string='Cotización', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Producto/Servicio', required=True)
    description = fields.Text('Descripción')
    quantity = fields.Float('Cantidad', default=1.0)
    price_unit = fields.Float('Precio Unitario')
    subtotal = fields.Float('Subtotal', compute='_compute_subtotal', store=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price
            self.description = self.product_id.name