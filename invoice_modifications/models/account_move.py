# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_number = fields.Char('Invoice Number')
    invoice_date = fields.Datetime('Invoice Date')
