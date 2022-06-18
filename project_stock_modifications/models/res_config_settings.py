# -*- coding: utf-8 -*-

from odoo import models, fields, api
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    location_dest_id = fields.Many2one('stock.location', "Project Location")
    post_journal_entry = fields.Boolean(string='Post Journal Entries')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            location_dest_id=int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'project_stock_modifications.location_dest_id')),
            post_journal_entry=(self.env['ir.config_parameter'].sudo().get_param(
                'project_stock_modifications.post_journal_entry')),
            # shipment_goods_on_transit_account_id=int(
            #     self.env['ir.config_parameter'].sudo().get_param(
            #         'purchase_modifications.shipment_goods_on_transit_account_id')),

        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        location_dest_id = self.location_dest_id
        param.set_param('project_stock_modifications.location_dest_id',
                        location_dest_id.id)
        post_journal_entry = self.post_journal_entry and self.post_journal_entry or False
        param.set_param('project_stock_modifications.post_journal_entry', post_journal_entry)
        # sales_type_excluded_ids = self.sales_type_excluded_ids and self.sales_type_excluded_ids.ids or False
        # param.set_param('purchase_modifications.sales_type_excluded_ids', sales_type_excluded_ids)
        # forecasted_sales_period = self.forecasted_sales_period and self.forecasted_sales_period or False
        # param.set_param('purchase_modifications.forecasted_sales_period', forecasted_sales_period)
        # shipment_goods_on_transit_account_id = self.shipment_goods_on_transit_account_id
        # param.set_param('purchase_modifications.shipment_goods_on_transit_account_id',
        #                 shipment_goods_on_transit_account_id.id)

