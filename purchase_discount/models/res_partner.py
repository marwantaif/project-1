
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_supplierinfo_discount = fields.Float(
        string="Default Supplier Discount (%)",
        digits="Discount",
        help="This value will be used as the default one, for each new"
        " supplierinfo line depending on that supplier.",
    )
