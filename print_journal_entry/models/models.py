
from odoo import api, fields, models

class Move(models.Model):
    _inherit = 'account.move'



class Company(models.Model):
    _inherit = 'res.company'

    address_arabic = fields.Char()
    company_arabic = fields.Char()

class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    address_arabic = fields.Char(related='company_id.address_arabic', readonly=False)
    company_arabic = fields.Char(related='company_id.company_arabic', readonly=False)

