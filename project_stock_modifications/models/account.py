from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    project_id = fields.Many2one('project.project', string='Project', readonly=True)
    task_id = fields.Many2one('project.task', string='Task', readonly=True)
