import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class ImportResultsWizard(models.TransientModel):
    _name = 'import.results.wizard'
    _description = 'Import Results Wizard'

    api_token = fields.Char(string='API Token', required=True)

    def action_import_results(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('form_editor.api_url')
        if not base_url:
            raise UserError('Form Editor API URL is not configured. Please set it in the system parameters.')

        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            response = requests.get(f'{base_url}/api/v1/templates', headers=headers)
            response.raise_for_status()
            templates = response.json()

            for template_data in templates:
                template = self.env['form.editor.template'].search([('name', '=', template_data['title'])], limit=1)
                if not template:
                    template = self.env['form.editor.template'].create({
                        'name': template_data['title'],
                        'author': template_data['author'],
                    })

                template.total_responses = template_data['total_responses']

                for question_data in template_data['questions']:
                    question = self.env['form.editor.question'].search([
                        ('template_id', '=', template.id),
                        ('question_text', '=', question_data['text'])
                    ], limit=1)

                    if not question:
                        question = self.env['form.editor.question'].create({
                            'template_id': template.id,
                            'question_text': question_data['text'],
                            'question_type': question_data['type'],
                        })

                    question.write({
                        'number_of_answers': question_data['number_of_answers'],
                        'average_number': question_data.get('average_number', 0),
                        'min_number': question_data.get('min_number', 0),
                        'max_number': question_data.get('max_number', 0),
                        'popular_answers': ', '.join(question_data.get('popular_answers', [])),
                    })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'Templates and results imported successfully',
                    'type': 'success',
                }
            }
        except requests.RequestException as e:
            raise UserError(f'Error importing results: {str(e)}')