from odoo import models, fields, api


class FormEditorTemplate(models.Model):
    _name = 'form.editor.template'
    _description = 'Form Editor Template'

    name = fields.Char(string='Template Title', required=True)
    author = fields.Char(string='Author', required=True)
    question_ids = fields.One2many('form.editor.question', 'template_id', string='Questions')
    total_responses = fields.Integer(string='Total Responses', default=0)