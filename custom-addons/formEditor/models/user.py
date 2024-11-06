from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    api_token = fields.Char(string='API Token', copy=False)