# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectStockModifications(http.Controller):
#     @http.route('/project_stock_modifications/project_stock_modifications', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_stock_modifications/project_stock_modifications/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_stock_modifications.listing', {
#             'root': '/project_stock_modifications/project_stock_modifications',
#             'objects': http.request.env['project_stock_modifications.project_stock_modifications'].search([]),
#         })

#     @http.route('/project_stock_modifications/project_stock_modifications/objects/<model("project_stock_modifications.project_stock_modifications"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_stock_modifications.object', {
#             'object': obj
#         })
