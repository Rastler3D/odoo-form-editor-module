# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FormEditorQuestion(models.Model):
    _name = 'form.editor.question'
    _description = 'Form Editor Question'

    template_id = fields.Many2one('form.editor.template', string='Template', required=True)
    question_text = fields.Text(string='Question Text', required=True)
    question_type = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('choice', 'Multiple Choice'),
    ], string='Question Type', required=True)
    number_of_answers = fields.Integer(string='Number of Answers', default=0)

    # Aggregated results
    average_number = fields.Float(string='Average (Number)', digits=(10, 2))
    min_number = fields.Float(string='Minimum (Number)', digits=(10, 2))
    max_number = fields.Float(string='Maximum (Number)', digits=(10, 2))
    popular_answers = fields.Text(string='Popular Answers (Text/Choice)')