# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.exceptions import ValidationError


class AccountVoucher(models.Model):
    _name = 'account.voucher'
    _description = 'Accounting Voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    def account_voucher_tax_domain(self):
        tax_domain = []
        if self._context.get('default_voucher_type'):
            type_id = self._context['default_voucher_type']
            if type_id:
                if type_id == 'in':
                    tax_domain = [('type_tax_use', 'in', ['sale', 'none'])]
                else:
                    tax_domain = [('type_tax_use', 'in', ['purchase', 'none'])]
        return tax_domain

    name = fields.Char("Accounting Voucher")
    voucher_type = fields.Selection([('in', 'Receipt'), ('out', 'Payment')], "Voucher Type", required=True,
                                    tracking=True)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True, states={'draft': [('readonly', False)]},
                                  required=True, tracking=True,
                                  default=lambda self: self.env.company.currency_id)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    description = fields.Char('Description', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(string='Date', required=True, index=True, readonly=True, tracking=True,
                       states={'draft': [('readonly', False)]}, copy=False, default=fields.Date.context_today)
    voucher_line_ids = fields.One2many('account.voucher.line', 'account_voucher_id', "Voucher Items", readonly=True,
                                       states={'draft': [('readonly', False)]})
    journal_id = fields.Many2one('account.journal', "Journal", check_company=True, readonly=True, required=True,
                                 states={'draft': [('readonly', False)]}, tracking=True,
                                 domain=[('type', 'in', ['cash', 'bank'])])
    account_id = fields.Many2one('account.account', related='journal_id.default_account_id', store=True, readonly=True)
    move_id = fields.Many2one('account.move', "Journal Entry")
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True,
                                 compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount')
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True,
                                     compute='_compute_amount')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          check_company=True)
    tax_id = fields.Many2one('account.tax', domain=account_voucher_tax_domain, check_company=True)

    @api.model
    def create(self, vals):
        if vals['voucher_type']:
            if vals['voucher_type'] == 'in':
                vals['name'] = "AVCHR/%s/%s" % (
                    dict(self._fields['voucher_type'].selection).get(vals.get('voucher_type'))
                    , self.env['ir.sequence'].sudo().next_by_code('account.voucher.receipt'))
            if vals['voucher_type'] == 'out':
                vals['name'] = "AVCHR/%s/%s" % (
                    dict(self._fields['voucher_type'].selection).get(vals.get('voucher_type'))
                    , self.env['ir.sequence'].sudo().next_by_code('account.voucher.payment'))
        val = super(AccountVoucher, self).create(vals)
        return val

    @api.onchange('voucher_line_ids')
    @api.depends('voucher_line_ids.amount')
    def _compute_amount(self):
        total_tax = 0.0
        for voucher in self:
            for line in voucher.voucher_line_ids:
                if line.tax_id:
                    total_tax += line.amount * (line.tax_id.amount / 100)
            voucher.amount_tax = total_tax
            total_untaxed = sum(line.amount for line in voucher.voucher_line_ids)
            voucher.amount_untaxed = total_untaxed
            total = total_tax + total_untaxed
            voucher.amount_total = total

    def action_post(self):
        move_obj = self.env['account.move']
        for voucher in self:
            if voucher.state == 'draft':
                move_vals = voucher._prepare_move_values()
                move = move_obj.sudo().create(move_vals)
                if move:
                    move.post()
                    voucher.move_id = move.id
                    voucher.state = 'posted'
                else:
                    raise ValidationError(_('Something went wrong while creating move!!!'))

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def _prepare_move_values(self):

        self.ensure_one()
        if self.description:
            name = self.description
        else:
            name = self.name
        move_line_src = {
            'name': name,
            'quantity': 1,
            'debit': self.amount_total if self.voucher_type == 'in' else 0,
            'credit': self.amount_total if self.voucher_type == 'out' else 0,
            'account_id': self.account_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'account_voucher_id': self.id,
            'currency_id': self.currency_id.id,
        }
        move_line_tax = {}
        if self.amount_tax > 0:
            if self.tax_id:
                move_line_tax = {
                    'name': name,
                    'quantity': 1,
                    'debit': self.amount_tax if self.voucher_type == 'out' else 0,
                    'credit': self.amount_tax if self.voucher_type == 'in' else 0,
                    'account_id': self.tax_id.invoice_repartition_line_ids.account_id.id,
                    'analytic_account_id': self.analytic_account_id.id,
                    'account_voucher_id': self.id,
                    'currency_id': self.currency_id.id,
                }
            else:
                raise ValidationError(_('Please Choose a Tax !'))
        move_lines = self.voucher_line_ids._get_account_move_line_values()
        move_lines.append((0, 0, move_line_src))
        if move_line_tax:
            move_lines.append((0, 0, move_line_tax))
        print("MOVE VALS:: ", move_lines)
        move_values = {
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'date': self.date,
            'ref': self.description,
            'account_voucher_id': self.id,
            'name': '/',
            'line_ids': move_lines
        }
        return move_values


class AccountVoucherLine(models.Model):
    _name = 'account.voucher.line'
    _description = 'Accounting Voucher Line'
    _check_company_auto = True

    @api.onchange('account_voucher_type_id')
    def account_voucher_type_domains(self):
        tax_domain = partner_domain = []
        type_id = self.account_voucher_type_id

        if type_id:
            account_id = False
            if type_id.account_id:
                account_id = type_id.account_id.id

            self.account_id = account_id
            self.description = self.account_voucher_id.description
            if type_id.voucher_type:
                if type_id.voucher_type == 'in':
                    tax_domain = [('type_tax_use', 'in', ['sale', 'none'])]
                else:
                    tax_domain = [('type_tax_use', 'in', ['purchase', 'none'])]
            if type_id.partner_type:
                if type_id.partner_type in ['customer_rank', 'supplier_rank']:
                    partner_domain = [(type_id.partner_type, '!=', 0)]
                elif type_id.partner_type == 'employee':
                    employee_partners = self.env['res.partner'].search([('employee_id', '!=', False)])
                    partner_domain = [('id', 'in', list(set(employee_partners.ids)))]
            return {'domain': {'tax_id': tax_domain, 'partner_id': partner_domain}}

    account_voucher_id = fields.Many2one('account.voucher', "Account Voucher")
    voucher_type = fields.Selection(related='account_voucher_id.voucher_type')
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', readonly=True, states={'draft': [('readonly', False)]},
                                  required=True, tracking=True,
                                  default=lambda self: self.env.company.currency_id)
    description = fields.Char('Description')
    amount = fields.Monetary(string='Amount', default=0.0, currency_field='currency_id')
    account_voucher_type_id = fields.Many2one('account.voucher.type', "Type", required=True, tracking=True,
                                              domain="[('voucher_type', '=', voucher_type)]")
    account_id = fields.Many2one('account.account', string='Account', required=True)
    partner_id = fields.Many2one('res.partner', "Partner", domain=account_voucher_type_domains)
    partner_type = fields.Selection(related='account_voucher_type_id.partner_type')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
                                          check_company=True)
    tax_id = fields.Many2one('account.tax', domain=account_voucher_type_domains, check_company=True)
    tax_number = fields.Char(string="Tax ID")
    voucher_number = fields.Char('Voucher Number')
    voucher_date = fields.Date('Voucher Date')

    def _get_account_move_line_values(self):
        move_line_values = []
        for line in self:
            move_line_name = ""
            if line.description:
                move_line_name = line.description
            else:
                if line.partner_id:
                    move_line_name += line.partner_id.name + ': '
                if line.account_voucher_id:
                    move_line_name += line.account_voucher_id.name
            account_dst = line.account_id
            account_date = line.account_voucher_id.date or fields.Date.context_today()
            move_line_dst = (0, 0, {
                'name': move_line_name,
                'debit': line.amount if line.voucher_type == 'out' else 0,
                'credit': line.amount if line.voucher_type == 'in' else 0,
                'account_id': account_dst.id,
                'date_maturity': account_date,
                'currency_id': line.currency_id.id,
                'analytic_account_id': line.analytic_account_id.id,
                'account_voucher_id': line.account_voucher_id.id,
                'account_voucher_line_id': line.id,
                'partner_id': line.partner_id.id,
            })
            move_line_values.append(move_line_dst)

        return move_line_values


class AccountVoucherType(models.Model):
    _name = 'account.voucher.type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    name = fields.Char("Type", required=True)
    account_id = fields.Many2one('account.account', string='Account', index=False, ondelete="cascade",
                                 tracking=True, check_company=True)
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.company)
    voucher_type = fields.Selection([('in', 'Receipt'), ('out', 'Payment')], "Voucher Type", required=True,
                                    tracking=True)
    partner_type = fields.Selection([('customer_rank', 'Customer'), ('supplier_rank', 'Vendor'),
                                     ('employee', 'Employee'), ('no_partner', 'No Partner')], "Partner Type",
                                    required=True, default='no_partner')
