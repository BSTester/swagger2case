import pytest
from loguru import logger
from pytest import raises
from swagger2case.core import SwaggerParser

class TestSwagger(object):

    def setup_class(self):
        self.swagger_parser = SwaggerParser("tests/data/demo.json")
        #self.method_value = self.swagger_parser.swagger_all_info["paths"]["/pet"]["post"]

    def get_method_value(self, urlpath, method):
        return self.swagger_parser.swagger_all_info["paths"].get(urlpath).get(method)

    def test_make_api_post_pet(self):
        api_dict = self.swagger_parser._make_api(
            "/pet",
            "post",
            self.get_method_value("/pet", "post"))
        logger.info(api_dict)

        assert "name" in api_dict[1]
        assert "request" in api_dict[1]
        assert "validate" in api_dict[1]

        validators_mapping = {
            validator["eq"][0]: validator["eq"][1]
            for validator in api_dict[1]["validate"]
        }

        assert validators_mapping["status_code"], '405'

    def test_make_request_url_put_pet_body(self):
        api_dict = {
            "request":{
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'put',
            self.get_method_value("/pet", "put"),
            '/pet')

        assert api_dict['request']['url'] == '/pet'


    def test_make_request_url_get_pet_findByStatus_query(self):
        api_dict = {
            "request": {
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'get',
            self.get_method_value("/pet/findByStatus", "get"),
            '/pet/findByStatus')

        assert api_dict['request']['url'] == '/pet/findByStatus'
        assert api_dict['request']['params'] == {'status': ''}

    def test_make_request_url_get_pet_petid_path(self):
        api_dict = {
            "request": {
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'get',
            self.get_method_value("/pet/{petId}", "get"),
            '/pet/{petId}')

        assert api_dict['request']['url'] == '/pet/$petId'
        assert api_dict['variables'] == {"petId": ""}

    def test_make_request_url_post_pet_petId_uploadImage_path(self):
        api_dict = {
            "request": {
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'post',
            self.get_method_value("/pet/{petId}/uploadImage", "post"),
            '/pet/{petId}/uploadImage')

        assert api_dict['request']['url'] == '/pet/$petId/uploadImage'
        assert api_dict['variables'] == {"petId": ""}

    def test_make_request_url_get_store_inventory_parameters_is_empty(self):
        api_dict = {
            "request": {
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'get',
            self.get_method_value("/store/inventory", "get"),
            '/store/inventory')

        assert api_dict['request']['url'] == '/store/inventory'
        assert api_dict['request']['params'] == {}

    def test_make_request_url_delete_store_order_orderId_path(self):
        api_dict = {
            "request": {
                "url": ''
            }
        }
        self.swagger_parser._make_request_url(
            api_dict,
            'delete',
            self.get_method_value("/store/order/{orderId}", "delete"),
            '/store/order/{orderId}')

        assert api_dict['request']['url'] == '/store/order/$orderId'
        assert api_dict['variables'] == {"orderId": ""}

    def test_make_request_data_post_pet_body(self):
        api_dict = {
            "request": {
                "data": {}
            }
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'post',
            self.get_method_value("/pet", "post")
        )

        assert api_dict['request']['data'] == {
            "id": "",
            "category": {
                "id": "",
                "name": ""
            },
            "name": "",
            "photoUrls": [],
            "tags": [],
            "status": ""}


