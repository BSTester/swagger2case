from swagger2case.core import SwaggerParser

class TestSwagger(object):

    def setup_class(self):
        self.swagger_parser = SwaggerParser()

    def test_make_api(self):
        swagger_paths_dict = load_swagger_api_paths(self.swagger_api_path)
        api_dict = self.swagger_parser._make_api("/pet", swagger_paths_dict["/pet"])
        assert "name" in api_dict
        assert "request" in api_dict
        assert "validate" in api_dict

        validators_mapping = {
            validator["eq"][0]: validator["eq"][1]
            for validator in api_dict["validate"]
        }
        assert validators_mapping["status_code"], 200
