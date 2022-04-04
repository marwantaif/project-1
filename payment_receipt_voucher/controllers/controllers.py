# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentReceiptVoucher(http.Controller):
#     @http.route('/payment_receipt_voucher/payment_receipt_voucher', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_receipt_voucher/payment_receipt_voucher/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_receipt_voucher.listing', {
#             'root': '/payment_receipt_voucher/payment_receipt_voucher',
#             'objects': http.request.env['payment_receipt_voucher.payment_receipt_voucher'].search([]),
#         })

#     @http.route('/payment_receipt_voucher/payment_receipt_voucher/objects/<model("payment_receipt_voucher.payment_receipt_voucher"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_receipt_voucher.object', {
#             'object': obj
#         })
