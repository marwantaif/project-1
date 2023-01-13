# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order.line'

    def copy_sale_order_line(self):
        self.copy(default={'order_id': self.order_id.id})


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def copy_purchase_order_line(self):
        self.copy(default={'order_id': self.order_id.id})

