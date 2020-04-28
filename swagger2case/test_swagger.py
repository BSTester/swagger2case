import pytest
from swagger2case.core import SwaggerParser

class TestSwagger(object):

    def setup_class(self):
        self.swagger_parser = SwaggerParser("tests/data/demo.json")
        self.method_value = self.swagger_parser.swagger_all_info["paths"]["/pet"]["post"]

    def test_make_api(self):
        api_dict = self.swagger_parser._make_api("/pet", "post", self.method_value)
        assert "name" in api_dict[1]
        assert "request" in api_dict[1]
        assert "validate" in api_dict[1]

        validators_mapping = {
            validator["eq"][0]: validator["eq"][1]
            for validator in api_dict["validate"]
        }
        assert validators_mapping["status_code"], 200
