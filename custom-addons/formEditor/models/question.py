from odoo import models, fields

class FormEditorQuestion(models.Model):
    _name = 'form.editor.question'
    _description = 'Form Editor Question'
    _order = 'sequence, id'

    template_id = fields.Many2one('form.editor.template', string='Template', required=True)
    type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Boolean'),
        ('select', 'Select')
    ], string='Type', required=True)
    title = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    options = fields.Text(string='Options')
    display_in_table = fields.Boolean(string='Display in Table', default=False)
    sequence = fields.Integer(string='Sequence', default=10)

    # Aggregation fields
    average_number = fields.Float(string='Average (Number)', digits=(10, 2))
    min_number = fields.Float(string='Minimum (Number)', digits=(10, 2))
    max_number = fields.Float(string='Maximum (Number)', digits=(10, 2))
    most_common_text = fields.Text(string='Most Common Text')
    unique_count_text = fields.Integer(string='Unique Text Count')
    true_count_boolean = fields.Integer(string='True Count (Boolean)')
    false_count_boolean = fields.Integer(string='False Count (Boolean)')
    option_counts = fields.Text(string='Option Counts (Select)')