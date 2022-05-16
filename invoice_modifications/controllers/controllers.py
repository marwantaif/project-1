# -*- coding: utf-8 -*-
# from odoo import http


# class InvoiceModifications(http.Controller):
#     @http.route('/invoice_modifications/invoice_modifications', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_modifications/invoice_modifications/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_modifications.listing', {
#             'root': '/invoice_modifications/invoice_modifications',
#             'objects': http.request.env['invoice_modifications.invoice_modifications'].search([]),
#         })

#     @http.route('/invoice_modifications/invoice_modifications/objects/<model("invoice_modifications.invoice_modifications"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_modifications.object', {
#             'object': obj
#         })
