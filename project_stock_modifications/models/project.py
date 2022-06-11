# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Project(models.Model):
    _inherit = 'project.project'

    picking_ids = fields.One2many('stock.picking', 'project_id', string='Transfers')
    delivered_count = fields.Integer(string='Delivered', compute='_compute_delivered_count')
    stock_account_id = fields.Many2one('account.account', string="Stock Account")
    product_account_id = fields.Many2one('account.account', string="Material Account")
    project_journal_id = fields.Many2one('account.journal', string="Project Journal")
    account_move_ids = fields.One2many('account.move', 'project_id', string='Journal Entries')
    account_move_count = fields.Integer(string='Journal Entries', compute='_compute_account_move_count')

    @api.depends('picking_ids')
    def _compute_delivered_count(self):
        for project in self:
            project.delivered_count = len(project.picking_ids)

    def _compute_account_move_count(self):
        for rec in self:
            rec.account_move_count = len(rec.account_move_ids)

    def action_stock_picking(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['project_id', '=', self.id]],
            "name": "Stock Picking",
        }

    def action_account_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['project_id', '=', self.id]],
            "name": "Account Move",
        }


class Task(models.Model):
    _inherit = 'project.task'

    @api.depends('estimated_material_ids.price_subtotal', 'consumed_material_ids.price_subtotal')
    def _amount_all(self):
        for task in self:
            estimated_total = consumed_total = 0.0
            for estimated_line in task.estimated_material_ids:
                estimated_total += estimated_line.price_subtotal
            for consumed_line in task.consumed_material_ids:
                consumed_total += consumed_line.price_subtotal
            task.update({
                'estimated_amount_total': estimated_total,
                'consumed_amount_total': consumed_total,
            })

    estimated_material_ids = fields.One2many('project.estimated.material', 'project_task_id',
                                             string="Estimated Material")
    consumed_material_ids = fields.One2many('project.consumed.material', 'project_task_id',
                                            string="Consumed Material")
    estimated_amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all')
    consumed_amount_total = fields.Monetary(string='Total', store=True, compute='_amount_all')
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True)
    picking_ids = fields.One2many('stock.picking', 'task_id', string='Transfers')
    delivered_count = fields.Integer(string='Delivered', compute='_compute_delivered_count')
    not_delivered_count = fields.Integer(string='Not Delivered', compute='_compute_not_delivered_count')
    picking_type_id = fields.Many2one('stock.picking.type', string='Stock Operation Type',
                                      domain="[('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)]",
                                      ondelete='restrict')
    account_move_ids = fields.One2many('account.move', 'task_id', string='Journal Entries')
    account_move_count = fields.Integer(string='Journal Entries', compute='_compute_account_move_count')

    def action_create_stock_picking(self):
        location_dest_id = int(self.env['ir.config_parameter'].sudo().get_param(
            'project_stock_modifications.location_dest_id', default=False))
        if not location_dest_id:
            raise ValidationError(
                _('You have to set a Projects Stock Location in settings'))
        for task in self:
            if task.consumed_material_ids:
                new_material = task.consumed_material_ids.filtered(lambda material: not material.picking_id)
                if new_material:
                    for line in new_material:
                        task_picking = self.env['stock.picking'].create({
                            'location_id': line.location_id.id,
                            'location_dest_id': location_dest_id,
                            'picking_type_id': line.picking_type_id.id,
                            'task_id': task.id,
                            'consumed_material_id': line.id,
                            'project_id': task.project_id.id,
                        })

                        task_move = self.env['stock.move'].create({
                            'name': 'move out',
                            'location_id': line.location_id.id,
                            'location_dest_id': location_dest_id,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_id.uom_id.id,
                            'product_uom_qty': line.quantity,
                            'picking_id': task_picking.id,
                        })
                        if task_move:
                            line.picking_id = task_picking.id
                        task_move.sudo()._action_assign()
                        task_move.sudo()._set_quantity_done(line.quantity)
                        task_move.sudo()._action_done()
                    task._create_inventory_account_move(new_material)

    def _create_inventory_account_move(self, new_material):
        move_line_vals = []
        post_journal_entry = (self.env['ir.config_parameter'].sudo().get_param(
            'project_stock_modifications.post_journal_entry', default=False))
        for rec in self:
            default_stock_account = rec.project_id.stock_account_id
            default_product_account = rec.project_id.product_account_id
            project_journal = rec.project_id.project_journal_id
            total_amount = 0.0
            if not project_journal or not default_stock_account:
                raise ValidationError(
                    _('You have to set a journal  and stock account for this project in the project setting'))
            for line in new_material:
                product_account = line.product_id.property_account_income_id
                if not product_account:
                    product_account = line.product_id.categ_id.property_account_income_categ_id
                    if not product_account:
                        product_account = default_product_account
                        if not default_product_account:
                            raise ValidationError(
                                _('No material account!, You have to set a material account'))
                total_amount += line.price_subtotal
                move_line_vals.append((0, 0, {
                    'name': line.product_id.display_name,
                    'debit': line.price_subtotal,
                    'credit': 0.0,
                    'account_id': product_account.id,
                    'project_id': rec.project_id.id,
                    'task_id': rec.id,
                    'analytic_account_id': rec.analytic_account_id.id or rec.project_id.analytic_account_id.id,

                }))
            move_line_vals.append((0, 0, {
                'name': rec.name,
                'debit': 0.0,
                'credit': total_amount,
                'account_id': default_stock_account.id,
                'project_id': rec.project_id.id,
                'task_id': rec.id,
            }))

            vals = {
                'journal_id': project_journal.id,
                'date': fields.datetime.today(),
                'project_id': rec.project_id.id,
                'task_id': rec.id,
                'state': 'draft',
                'line_ids': move_line_vals,
            }
            move = self.env['account.move'].create(vals)
            if post_journal_entry:
                move._post()

    @api.depends('picking_ids')
    def _compute_delivered_count(self):
        for task in self:
            task.delivered_count = len(task.picking_ids)

    @api.depends('consumed_material_ids')
    def _compute_not_delivered_count(self):
        for task in self:
            task.not_delivered_count = len(
                task.consumed_material_ids.filtered(lambda material: not material.picking_id))

    def _compute_account_move_count(self):
        for rec in self:
            rec.account_move_count = len(rec.account_move_ids)

    def action_stock_picking(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['task_id', '=', self.id]],
            "name": "Stock Picking",
        }

    def action_account_move(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['task_id', '=', self.id]],
            "name": "Account Move",
        }


class ProjectEstimatedMaterial(models.Model):
    _name = 'project.estimated.material'
    _description = 'Estimated Material'

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * line.quantity
            line.update({
                'price_subtotal': price,
            })

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float('Quantity', required=True)
    price_unit = fields.Monetary('Unit Price')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', readonly=True)
    project_task_id = fields.Many2one('project.task', string='Task')
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True)


class ProjectConsumedMaterial(models.Model):
    _name = 'project.consumed.material'
    _description = 'Consumed Material'

    @api.depends('quantity', 'price_unit')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * line.quantity
            line.update({
                'price_subtotal': price,
            })

    @api.model
    def _get_default_picking_type(self):
        task_id = self.env['project.task'].search([('id', '=', self.env.context.get('params', {}).get('id'))])
        return task_id.picking_type_id

    @api.onchange('picking_type_id')
    def _get_location_id(self):
        self.location_id = self.picking_type_id.default_location_src_id

    product_id = fields.Many2one('product.product', string="Product", required=True)
    quantity = fields.Float('Quantity', required=True)
    price_unit = fields.Monetary('Unit Price')
    price_subtotal = fields.Monetary(string='Subtotal', compute='_compute_amount', readonly=True)
    project_task_id = fields.Many2one('project.task', string='Task')
    company_id = fields.Many2one('res.company', 'Company', readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Picking', ondelete='restrict')
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type',
                                      domain="[('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', company_id)]",
                                      default=_get_default_picking_type,
                                      required=True, ondelete='restrict')
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=True, required=True)
