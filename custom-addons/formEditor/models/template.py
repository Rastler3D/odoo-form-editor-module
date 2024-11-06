from odoo import models, fields, api

class FormEditorTemplate(models.Model):
    _name = 'form.editor.template'
    _description = 'Form Editor Template'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    image = fields.Char(string='Image URL')
    creator_id = fields.Integer(string='Creator ID')
    created_by = fields.Char(string='Created By')
    created_at = fields.Datetime(string='Created At')
    topic = fields.Char(string='Topic')
    tags = fields.Many2many('form.editor.tag', string='Tags')
    access_setting = fields.Selection([
        ('All', 'All'),
        ('Specified', 'Specified'),
    ], string='Access Setting', default='public')
    allow_list = fields.Char(string='Allow List')
    likes = fields.Integer(string='Likes', default=0)
    filled_count = fields.Integer(string='Filled Count', default=0)
    question_ids = fields.One2many('form.editor.question', 'template_id', string='Questions')

    @api.depends('question_ids')
    def _compute_question_count(self):
        for template in self:
            template.question_count = len(template.question_ids)

    question_count = fields.Integer(string='Question Count', compute='_compute_question_count', store=True)

    def action_view_questions(self):
        self.ensure_one()
        return {
            'name': 'Questions',
            'type': 'ir.actions.act_window',
            'res_model': 'form.editor.question',
            'view_mode': 'tree,form',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

class FormEditorTag(models.Model):
    _name = 'form.editor.tag'
    _description = 'Form Editor Tag'

    name = fields.Char(string='Name', required=True)