from odoo import models, fields, api
import requests
import base64

class FormEditorTemplate(models.Model):
    _name = 'form.editor.template'
    _description = 'Form Editor Template'

    external_id = fields.Integer(string='External ID', required=True)
    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    image_url = fields.Char(string='Image URL')
    image = fields.Binary(string='Image', compute='_compute_image', store=True)
    creator_id = fields.Integer(string='Creator ID')
    created_by = fields.Char(string='Created By')
    created_at = fields.Datetime(string='Created At')
    topic = fields.Char(string='Topic')
    tags = fields.Many2many('form.editor.tag', string='Tags')
    access_setting = fields.Selection([
        ('All', 'All'),
        ('Specified', 'Specified'),
    ], string='Access Setting', default='All')
    allow_list = fields.Char(string='Allow List')
    likes = fields.Integer(string='Likes', default=0)
    filled_count = fields.Integer(string='Filled Count', default=0)
    question_ids = fields.One2many('form.editor.question', 'template_id', string='Questions')

    @api.depends('image_url')
    def _compute_image(self):
        for record in self:
            record.image = False  # Default value if URL is empty or invalid
            if record.image_url:
                response = requests.get(record.image_url, timeout=5)
                if response.status_code == 200:
                    record.image = base64.b64encode(response.content)
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