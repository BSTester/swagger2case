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
            },
            "variables": {}
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
            },
            "variables": {}
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
                "url": "",
                "params": {}
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
            },
            "variables": {}
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
                "json": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'post',
            self.get_method_value("/pet", "post")
        )

        assert api_dict['request']['json'] == {
            "id": 0,
            "category": {
                "id": 0,
                "name": ""
            },
            "name": "",
            "photoUrls": [],
            "tags": [],
            "status": ""}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_put_pet_body(self):
        api_dict = {
            "request": {
                "json": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'put',
            self.get_method_value("/pet", "put")
        )

        assert api_dict['request']['json'] == {
            "id": 0,
            "category": {
                "id": 0,
                "name": ""
            },
            "name": "",
            "photoUrls": [],
            "tags": [],
            "status": ""}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_get_pet_findByStatus_query(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'get',
            self.get_method_value("/pet/findByStatus", "get")
        )

        assert api_dict['request']['data'] == {}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_post_pet_petId_uploadImage_formdata(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'post',
            self.get_method_value("/pet/{petId}/uploadImage", "post")
        )

        assert api_dict['request']['data'] == {
            'additionalMetadata': '',
            'file': ''
            }
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_get_store_inventory_parameters_is_empty(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'get',
            self.get_method_value("/store/inventory", "get")
        )

        assert api_dict['request']['data'] == {}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_post_store_order_body(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'post',
            self.get_method_value("/store/order", "post")
        )

        assert api_dict['request']['data'] == {
            'id': 0,
            'petId': 0,
            'quantity': 0,
            'shipDate': '',
            'status': '',
            'complete': False}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_make_request_data_delete_pet_petId_header(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'delete',
            self.get_method_value("/pet/{petId}", "delete")
        )

        assert api_dict['request']['data'] == {}
        assert api_dict['request']['headers'] == {"api_key": "$api_key"}
        assert api_dict['variables'] == {"api_key": ""}

    def test_make_request_data_post_pet_petId_formdata(self):
        api_dict = {
            "request": {
                "data": {},
                "headers": {}
            },
            "variables": {}
        }
        self.swagger_parser._make_request_data(
            api_dict,
            'post',
            self.get_method_value("/pet/{petId}", "post")
        )

        assert api_dict['request']['data'] == {"name": "", "status": ""}
        assert api_dict['request']['headers'] == {}
        assert api_dict['variables'] == {}

    def test_prepare_validate_post_pet_body(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/pet", "post")
        )
        assert api_dict['validate'] == [
            {"eq": ["status_code", '405']},
            {"eq": ["content.description", 'Invalid input']},
            {"eq": ["headers.Content-Type", "application/xml"]}]

    def test_prepare_validate_put_pet_body(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/pet", "put")
        )
        assert api_dict['validate'] == [
            {"eq": ["status_code", '400']},
            {'eq': ['content.description', 'Invalid ID supplied']},
            {"eq": ["status_code", '404']},
            {'eq': ['content.description', 'Pet not found']},
            {"eq": ["status_code", '405']},
            {'eq': ['content.description', 'Validation exception']},
            {"eq": ["headers.Content-Type", "application/xml"]}]

    def test_prepare_validate_get_pet_findByStatus_query(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/pet/findByStatus", "get")
        )

        assert api_dict['validate'] == [
            {"eq": ["status_code", '200']},
            {'eq': ['content.description', 'successful operation']},
            {"eq": ["content.id", 0]},
            {"eq": ["content.category.id", 0]},
            {"eq": ["content.category.name", '']},
            {"eq": ["content.name", '']},
            {"eq": ["content.photoUrls", []]},
            {"eq": ["content.tags", []]},
            {"eq": ["content.status", '']},
            {"eq": ["status_code", '400']},
            {'eq': ['content.description', 'Invalid status value']},
            {"eq": ["headers.Content-Type", "application/xml"]}]

    def test_prepare_validate_get_store_inventory_no_ref(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/store/inventory", "get")
        )

        assert api_dict['validate'] == [
            {"eq": ["status_code", '200']},
            {'eq': ['content.description', 'successful operation']},
            {"eq": ["headers.Content-Type", "application/json"]}]

    def test_prepare_validate_post_store_order_no_items(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/store/order", "post")
        )

        assert api_dict['validate'] == [
            {"eq": ["status_code", '200']},
            {'eq': ['content.description', 'successful operation']},
            {'eq': ['content.id', 0]},
            {'eq': ['content.petId', 0]},
            {'eq': ['content.quantity', 0]},
            {'eq': ['content.shipDate', '']},
            {'eq': ['content.status', '']},
            {'eq': ['content.complete', False]},
            {"eq": ["status_code", '400']},
            {'eq': ['content.description', 'Invalid Order']},
            {"eq": ["headers.Content-Type", "application/xml"]}]

    def test_prepare_validate_post_user_default(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/user", "post")
        )

        assert api_dict['validate'] == [
            {'eq': ['content.description', 'successful operation']},
            {"eq": ["headers.Content-Type", "application/xml"]}]

    def test_prepare_validate_get_user_login_headers(self):
        api_dict = {
            'validate': []
        }
        self.swagger_parser._prepare_validate(
            api_dict,
            self.get_method_value("/user/login", "get")
        )

        assert api_dict['validate'] == [
            {"eq": ["status_code", '200']},
            {'eq': ['content.description', 'successful operation']},
            {'eq': ['headers.X-Rate-Limit', 0]},
            {'eq': ['headers.X-Expires-After', '']},
            {"eq": ["status_code", '400']},
            {'eq': ['content.description', 'Invalid username/password supplied']},
            {"eq": ["headers.Content-Type", "application/xml"]}]




