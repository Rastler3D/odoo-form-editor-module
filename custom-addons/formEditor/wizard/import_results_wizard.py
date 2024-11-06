from odoo import models, fields, api
import requests
from odoo.exceptions import UserError
from datetime import datetime

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
                    template = self.env['form.editor.template'].create(self._prepare_template_values(template_data))
                else:
                    template.write(self._prepare_template_values(template_data))

                for index, question_data in enumerate(template_data['questions']):
                    question = self.env['form.editor.question'].search([
                        ('template_id', '=', template.id),
                        ('external_id', '=', question_data['id'])
                    ], limit=1)

                    if not question:
                        self.env['form.editor.question'].create(self._prepare_question_values(question_data, index, template.id))
                    else:
                        question.write(self._prepare_question_values(question_data, index))

                # Fetch aggregation data
                agg_response = requests.get(f'{base_url}/api/Template/{template_data["id"]}/aggregation', headers=headers)
                agg_response.raise_for_status()
                agg_data = agg_response.json()

                self._update_aggregation(template_data, agg_data)

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
            'external_id': template_data['id'],
            'description': template_data['description'],
            'topic': template_data['topic'],
            'image': template_data.get('image'),
            'creator_id': template_data['creatorId'],
            'created_by': template_data['createdBy'],
            'created_at': datetime.fromisoformat(template_data['createdAt'].replace('Z', '+00:00')).replace(tzinfo=None),
            'tags': [(6, 0, self._get_or_create_tags(template_data['tags']))],
            'access_setting': template_data['accessSetting'],
            'allow_list': ','.join(map(str, template_data.get('allowList', []))),
            'filled_count': template_data['filledCount'],
            'likes': template_data['likes'],
        }
    def _get_or_create_tags(self, tag_names):
        tag_ids = []
        for tag_name in tag_names:
            tag = self.env['form.editor.tag'].search([('name', '=', tag_name)], limit=1)
            if not tag:
                tag = self.env['form.editor.tag'].create({'name': tag_name})
            tag_ids.append(tag.id)
        return tag_ids

    def _prepare_question_values(self, question_data, order, template_id=None):
        values = {
            'external_id': question_data['id'],
            'title': question_data['title'],
            'type': question_data['type'],
            'options': '\n'.join(question_data.get('options', [])),
            'display_in_table': question_data['displayInTable'],
            'description': question_data['description'],
            'order': order,
        }
        if template_id:
            values['template_id'] = template_id
        return values

    def _update_aggregation(self, template, agg_data):
        for question_id, aggregation in agg_data['questions'].items():
            question = self.env['form.editor.question'].search([
                ('template_id', '=', template["id"]),
                ('external_id', '=', int(question_id))
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
                    'option_counts_select': self._format_option_counts(aggregation.get('optionCountsSelect', [])),
                })

    def _format_option_counts(self, option_counts):
        return '\n'.join([f"{option['option']}: {option['count']}" for option in option_counts])