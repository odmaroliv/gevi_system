from odoo import models, fields, api

class AssignTechnicianWizard(models.TransientModel):
    _name = 'assign.technician.wizard'
    _description = 'Asignar Técnico a Orden de Servicio'

    service_order_id = fields.Many2one('service.order', string='Orden de Servicio', required=True)
    technician_id = fields.Many2one('hr.employee', string='Técnico', required=True, domain=[('is_technician', '=', True)])
    scheduled_date = fields.Datetime('Fecha Programada', required=True)

    def action_assign_technician(self):
        self.ensure_one()
        self.service_order_id.write({
            'technician_id': self.technician_id.id,
            'scheduled_date': self.scheduled_date,
            'state': 'scheduled'
        })
        self.env['service.visit'].create({
            'service_order_id': self.service_order_id.id,
            'technician_id': self.technician_id.id,
            'scheduled_date': self.scheduled_date,
        })
        return {'type': 'ir.actions.act_window_close'}