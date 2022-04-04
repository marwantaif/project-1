# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    account_voucher_id = fields.Many2one('account.voucher', "Accounting Voucher")


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    account_voucher_id = fields.Many2one('account.voucher', "Accounting Voucher")
    account_voucher_line_id = fields.Many2one('account.voucher.line', "Voucher Line")
