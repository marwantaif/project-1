from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    task_id = fields.Many2one('project.task', string="Task")
    consumed_material_id = fields.Many2one('project.consumed.material', string="Consumed Material", ondelete='restrict')
    project_id = fields.Many2one("project.project", string="Project")
