# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
from odoo import api, fields, models


class CoAPrintTemplate(models.AbstractModel):
    _name = "report.account_parent.report_coa_hierarchy_print"
    _description = "CoA Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        wiz_id = data.get('wiz_id')
        coa = self.env['account.open.chart'].browse(wiz_id)
        report_data = coa.get_pdf(wiz_id)
        return {
            'doc_ids': docids,
            'doc_model': data.get('context', {}).get('active_model'),
            # 'data': report_data,
            **report_data
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
