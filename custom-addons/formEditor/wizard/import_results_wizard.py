from odoo import models, fields, api
import requests
from odoo.exceptions import UserError

class ImportResultsWizard(models.TransientModel):
    _name = 'import.results.wizard'
    _description = 'Import Results Wizard'

    api_token = fields.Char(string='API Token', required=True)

    def action_import_results(self):
        user = self.env.user
        user.api_token = self.api_token

        base_url = self.env['ir.config_parameter'].sudo().get_param('form_editor.api_url')
        if not base_url:
            raise UserError('Form Editor API URL is not configured. Please set it in the system parameters.')

        headers = {'X-API-Token': f'{self.api_token}'}

        try:
            # Fetch current user
            user_response = requests.get(f'{base_url}/api/User/me', headers=headers)
            user_response.raise_for_status()
            current_user = user_response.json()

            # Fetch user templates
            templates_response = requests.get(f'{base_url}/api/Template/user/{current_user["id"]}?pageSize=-1', headers=headers)
            templates_response.raise_for_status()
            templates = templates_response.json().get('data', [])

            for template_data in templates:
                template = self.env['form.editor.template'].search([('name', '=', template_data['name'])], limit=1)
                if not template:
                    template = self.env['form.editor.template'].create({
                        'name': template_data['name'],
                        'description': template_data['description'],
                        'author_id': user.id,
                    })

                for question_data in template_data['questions']:
                    question = self.env['form.editor.question'].search([
                        ('template_id', '=', template.id),
                        ('question_text', '=', question_data['title'])
                    ], limit=1)

                    if not question:
                        self.env['form.editor.question'].create({
                            'template_id': template.id,
                            'question_text': question_data['title'],
                            'question_type': question_data['type'],
                        })

                # Fetch aggregation data
                agg_response = requests.get(f'{base_url}/api/Template/{template_data["id"]}/aggregation', headers=headers)
                agg_response.raise_for_status()
                agg_data = agg_response.json()

                for question_id, aggregation in agg_data['questions'].items():
                    question = self.env['form.editor.question'].search([
                        ('template_id', '=', template.id),
                        ('question_text', '=', question_id)
                    ], limit=1)

                    if question:
                        question.write({
                            'average_number': aggregation.get('averageNumber'),
                            'min_number': aggregation.get('minNumber'),
                            'max_number': aggregation.get('maxNumber'),
                            'most_common_text': aggregation.get('mostCommonText'),
                            'unique_count_text': aggregation.get('uniqueCountText'),
                            'true_count_boolean': aggregation.get('trueCountBoolean'),
                            'false_count_boolean': aggregation.get('falseCountBoolean'),
                            'option_counts': str(aggregation.get('optionCountsSelect')),
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