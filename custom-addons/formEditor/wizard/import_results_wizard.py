import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class ImportResultsWizard(models.TransientModel):
    _name = 'import.results.wizard'
    _description = 'Import Results Wizard'

    api_token = fields.Char(string='API Token', required=True)
    user_id = fields.Integer(string='User ID', required=True)

    def action_import_results(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('form_editor.api_url')
        if not base_url:
            raise UserError('Form Editor API URL is not configured. Please set it in the system parameters.')

        headers = {'Authorization': f'Bearer {self.api_token}'}

        try:
            # Fetch user templates
            response = requests.get(f'{base_url}/api/Template/user/{self.user_id}', headers=headers)
            response.raise_for_status()
            templates = response.json().get('data', [])

            for template_info in templates:
                # Fetch full template data
                template_response = requests.get(f'{base_url}/api/Template/{template_info["id"]}', headers=headers)
                template_response.raise_for_status()
                template_data = template_response.json()

                template = self.env['form.editor.template'].search([('name', '=', template_data['name'])], limit=1)
                if not template:
                    template = self.env['form.editor.template'].create(self._prepare_template_values(template_data))
                else:
                    template.write(self._prepare_template_values(template_data))

                # Create or update questions
                for question_data in template_data['questions']:
                    question = self.env['form.editor.question'].search([
                        ('template_id', '=', template.id),
                        ('title', '=', question_data['title'])
                    ], limit=1)

                    if question:
                        question.write(self._prepare_question_values(question_data))
                    else:
                        self.env['form.editor.question'].create(self._prepare_question_values(question_data, template.id))

                # Fetch and update aggregated results
                agg_response = requests.get(f'{base_url}/api/Template/{template_data["id"]}/aggregation', headers=headers)
                agg_response.raise_for_status()
                agg_data = agg_response.json()

                self._update_aggregation(template, agg_data)

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

    def _prepare_template_values(self, template_data):
        return {
            'name': template_data['name'],
            'description': template_data['description'],
            'image': template_data.get('image'),
            'creator_id': template_data['creatorId'],
            'created_by': template_data['createdBy'],
            'created_at': template_data['createdAt'],
            'topic': template_data['topic'],
            'tags': [(6, 0, self._get_or_create_tags(template_data['tags']))],
            'access_setting': template_data['accessSetting'].lower(),
            'allow_list': ','.join(map(str, template_data.get('allowList', []))),
            'likes': template_data['likes'],
            'filled_count': template_data['filledCount'],
        }

    def _get_or_create_tags(self, tag_names):
        tag_ids = []
        for tag_name in tag_names:
            tag = self.env['form.editor.tag'].search([('name', '=', tag_name)], limit=1)
            if not tag:
                tag = self.env['form.editor.tag'].create({'name': tag_name})
            tag_ids.append(tag.id)
        return tag_ids

    def _prepare_question_values(self, question_data, template_id=None):
        values = {
            'title': question_data['title'],
            'type': question_data['type'].lower(),
            'description': question_data['description'],
            'options': '\n'.join(question_data.get('options', [])),
            'display_in_table': question_data['displayInTable'],
        }
        if template_id:
            values['template_id'] = template_id
        return values

    def _update_aggregation(self, template, agg_data):
        for question_id, aggregation in agg_data['questions'].items():
            question = self.env['form.editor.question'].search([
                ('template_id', '=', template.id),
                ('title', '=', question_id)
            ], limit=1)

            if question:
                question.write({
                    'average_number': aggregation.get('averageNumber', 0),
                    'min_number': aggregation.get('minNumber', 0),
                    'max_number': aggregation.get('maxNumber', 0),
                    'most_common_text': aggregation.get('mostCommonText', ''),
                    'unique_count_text': aggregation.get('uniqueCountText', 0),
                    'true_count_boolean': aggregation.get('trueCountBoolean', 0),
                    'false_count_boolean': aggregation.get('falseCountBoolean', 0),
                    'option_counts': self._format_option_counts(aggregation.get('optionCountsSelect', [])),
                })

    def _format_option_counts(self, option_counts):
        return '\n'.join([f"{option['option']}: {option['count']}" for option in option_counts])