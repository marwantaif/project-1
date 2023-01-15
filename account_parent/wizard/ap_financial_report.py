##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import time
from odoo.exceptions import UserError
from markupsafe import Markup

class OpenAccountChart(models.TransientModel):
	"""
	For Chart of Accounts
	"""
	_inherit = "account.open.chart"
