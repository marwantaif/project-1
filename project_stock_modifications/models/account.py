from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('project_id')
    def _task_id_domain(self):
        for rec in self:
            if rec.project_id:
                task_domain = [('project_id', '=', rec.project_id.id)]
                rec.task_id = False
                return {'domain': {'task_id': task_domain}}

    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('project_id')
    def _task_id_domain(self):
        for rec in self:
            if rec.project_id:
                task_domain = [('project_id', '=', rec.project_id.id)]
                rec.task_id = False
                return {'domain': {'task_id': task_domain}}

    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')
