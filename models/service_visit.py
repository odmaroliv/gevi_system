from odoo import models, fields, api

class ServiceVisit(models.Model):
    _name = 'service.visit'
    _description = 'Visita de Servicio'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Referencia', required=True, copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('service.visit'))
    service_order_id = fields.Many2one('service.order', string='Orden de Servicio', required=True)
    partner_id = fields.Many2one('res.partner', related='service_order_id.partner_id', string='Cliente', store=True)
    technician_id = fields.Many2one('hr.employee', string='Técnico', required=True)
    scheduled_date = fields.Datetime('Fecha Programada', required=True)
    actual_start = fields.Datetime('Inicio Real')
    actual_end = fields.Datetime('Fin Real')
    state = fields.Selection([
        ('scheduled', 'Programada'),
        ('in_progress', 'En Proceso'),
        ('done', 'Finalizada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='scheduled', tracking=True)
    notes = fields.Text('Notas')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user)

    def action_start(self):
        self.write({'state': 'in_progress', 'actual_start': fields.Datetime.now()})

    def action_done(self):
        self.write({'state': 'done', 'actual_end': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.model
    def create(self, vals):
        visit = super(ServiceVisit, self).create(vals)
        visit.service_order_id.write({'state': 'scheduled'})
        return visit