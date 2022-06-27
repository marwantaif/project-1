# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class AccountVoucherLine(models.Model):
    _inherit = 'account.voucher.line'

    @api.onchange('project_id')
    def _task_id_domain(self):
        for rec in self:
            if rec.project_id:
                task_domain = [('project_id', '=', rec.project_id.id)]
                rec.task_id = False
                return {'domain': {'task_id': task_domain}}

    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')

    def _get_account_move_line_values(self):
        res = super(AccountVoucherLine, self)._get_account_move_line_values()
        if res:
            if self.project_id:
                res[0][2].update({
                    'project_id': self.project_id.id
                })
            if self.task_id:
                res[0][2].update({
                    'task_id': self.task_id.id
                })
        return res
