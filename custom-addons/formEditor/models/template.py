from odoo import models, fields, api

class FormEditorTemplate(models.Model):
    _name = 'form.editor.template'
    _description = 'Form Editor Template'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    author_id = fields.Many2one('res.users', string='Author', required=True)
    question_ids = fields.One2many('form.editor.question', 'template_id', string='Questions')
    filled_count = fields.Integer(string='Number of Answers', default=0)