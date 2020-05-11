import pytest
from loguru import logger
from swagger2case.utils import get_related_tag_definitions_content, load_swagger_api

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
