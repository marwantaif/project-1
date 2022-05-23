# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    invoice_number = fields.Char('Invoice Number')
    invoice_date = fields.Datetime('Invoice Date')
    price_subtotal_tax = fields.Float(compute='_compute_price_tax', string=' Total including tax', store=True)

    @api.depends('price_unit', 'discount', 'quantity',
                 'product_id')
    def _compute_price_tax(self):
        for line in self:

            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            tax_amount = 0
            total_excluded = price * line.quantity
            if line.tax_ids:

                for tax in line.tax_ids:
                    taxes = tax.compute_all(price, line.currency_id, line.quantity, product=line.product_id,
                                            partner=line.partner_id)
                    if taxes:
                        tax_amount += taxes['total_included'] - taxes['total_excluded']

            line.price_subtotal_tax = tax_amount + total_excluded

            # if line.currency_id:
            #     line.price_subtotal_tax = round(line.price_subtotal_tax, 4)
