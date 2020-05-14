import pytest
from loguru import logger
from swagger2case.utils import get_related_tag_definitions_content, load_swagger_api, generate_validate_content

class TestUtils(object):


    def test_get_related_tag_definitions_content(self):

        swagger_file_content = load_swagger_api("tests/data/demo.json")

        tag_content = get_related_tag_definitions_content(swagger_file_content, 'pet')

        assert tag_content == {
            'id': 0,
            'category': {
                'id': 0,
                'name': ''
            },
            'name': '',
            'photoUrls': [],
            'tags': [],
            'status': ''}

    def test_generate_validate_content_with_definitions(self):
        definitions_dict = {
            "id": 0,
            "category": {
                "id": 0,
                "name": ""
            },
            "name": "",
            "photoUrls": [],
            "tags": [],
            "status": ""}

        validate_content = generate_validate_content(definitions_dict)
        logger.exception(validate_content)
        assert validate_content == [
                {"eq": ["content.id", 0]},
                {"eq": ["content.category.id", 0]},
                {"eq": ["content.category.name", '']},
                {"eq": ["content.name", '']},
                {"eq": ["content.photoUrls", []]},
                {"eq": ["content.tags", []]},
                {"eq": ["content.status", '']},

        ]
