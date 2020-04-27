from swagger2case import utils
import re
from loguru import logger
import sys

class SwaggerParser(object):

    def __init__(self, swagger_file_path, filter_str=None, exclude_str=None):
        self.swagger_file_path = swagger_file_path
        self.filter_str = filter_str
        self.exclude_str = exclude_str or ""


    # def gen_api(self, filt_type=json):
    #     #create
    #     _make_dirctionar_for_tags(tags_list)
    #     apis_list = _make_apis(paths_dict)  #api have exists correct dir
    #     for api in apis_list:
    #         #api = {'tag_name', 'api_dict'}
    #         if file_type = json:
    #             utils.dump_json(api.api_dict, "api/pet/xxx.json")
    #         else
    #             utils.dump_yaml(api.api_dict, new_file_path)



    def get_swagger_all_info(self):
        return load_swagger_api(self.swagger_file_path)


    def _gen_apis(self):
        """ make api list.
            api list are parsed from swagger paths dict.

        """
        def is_exclude(url, exclude_str):
            exclude_str_list = exclude_str.split("|")
            for exclude_str in exclude_str_list:
                if exclude_str and exclude_str in url:
                    return True

            return False

        api_all_list = []
        swagger_all_info = load_swagger_api(self.swagger_file_path)
        # host = swagger_all_info['host']
        # basepath = swagger_all_info['basePath']
        paths_dict = swagger_all_info['paths']
        for key, value in paths_dict:

            if self.filter_str and self.filter_str not in key:
                continue

            if is_exclude(key, self.exclude_str):
                continue

            else:
                api_list = self._make_apis_for_urlpath(key, value)
                api_all_list.append(api_list)
        return api_all_list

    def _make_apis_for_urlpath(self, urlpath, urlpath_value):
        """ extract info from urlpath dict and make apis
        """
        api_list = [()]
        for method , method_value in urlpath_value:
            (tag_name, api_dict) = self._make_api(urlpath, method, method_value)
            api_list.append((tag_name, api_dict))
        return api_list

    def _make_api(self, urlpath, method, method_value):
        """ extract info from path dict and make api

                Args:
                    {
                        "post": {
                        "tags": [
                            "pet"
                        ],
                        "summary": "Add a new pet to the store",
                        "description": "",
                        "operationId": "addPet",
                        "consumes": [
                            "application/json"],
                        "produces": [
                            "application/json" ],
                        "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "description": "Pet object that needs to be added to the store",
                            "required": true,
                            "schema": {
                                "$ref": "#/definitions/Pet"
                            }
                        }],
                       "responses": {
                           "405": {
                               "description": "Invalid input"
                           }
                       },
                       "security": [
                       {
                           "petstore_auth": [
                               "write:pets",
                               "read:pets"
                           ]
                       }]
                    },
        """

        api_dict = {
            "name": "",
            "variables": {},
            "request": {},
            "base_url": "",
            "validate": []
        }
        tag_name = method_value['tags'][0]
        self._prepare_name(api_dict, method_value)
        self._prepare_baseurl(api_dict)
        self._prepare_variables(api_dict, method_value)
        self._prepare_request(api_dict, method, method_value, urlpath)
        self._prepare_validate(api_dict, method_value)
        return (tag_name, api_dict)

    def _prepare_name(self, api_dict, method_value):
        """ parser operationId info from path dict and make name of api
        """
        api_dict['name'] = method_value['operationId']

    def _prepare_variables(self, api_dict, method_value):
        pass

    def _prepare_validate(self, api_dict, method_value):
        pass

    def _prepare_request(self,api_dict, method, method_value, urlpath):
        """ extract info from path dict and make request.

            Args:
                "/pet": {
                    "post": {
                    "summary": "Add a new pet to the store",
                    "consumes": [
                        "application/json"],
                    "produces": [
                        "application/json" ],
                    "parameters": [
                    {
                        "in": "body",
                        "name": "body",
                        "description": "Pet object that needs to be added to the store",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/Pet"
                        }
                    }],
                },
        """

        self._make_request_url(api_dict, method, method_value, urlpath)
        self._make_request_method(api_dict, method)
        self._make_request_headers(api_dict, method_value)
        self._make_request_data(api_dict, method_value)

    def _make_request_url(self, api_dict, method, method_value, urlpath):
        """ parse url and parameters, and make url and params of api request

                Args:
                    "/pet/findByStatus": {
                        "get": {
                          "parameters": [
                            {
                              "name": "status",
                              "in": "query",
                              "required": true,
                              "type": "array",
                              "items": {
                                "type": "string",
                                "enum": [
                                  "available",
                                  "pending",
                                  "sold"
                                ],
                                "default": "available"
                              },
                              "collectionFormat": "multi"
                            }
                          ],
                        }
                Returns:
                    {
                        "request": {
                            url: "/pet/findByStatus",
                            params: {"status": "sold"}
                        }
                    }

                    {
                        "request": {
                            url: "/pet/$petid",
                        }
                    }

        """
        if re.search(r'\{.*\}', urlpath):
            urlpath = re.sub(r'\{.*\}', '\$.*', urlpath)
        else:
            for key, value in method_value:
                if method != 'get':
                    break
                else:
                    if 'parameters' in method_value:
                        params = {}
                        for parameter in value['parameters']:
                            parameter_key = parameter['name']
                            parameter_value = ""
                            params.update({parameter_key, parameter_value})
                        api_dict['request']['url'] = urlpath
                        api_dict['request']['params'] = params
                    else:
                        logger.error("url missed paramters in request.")
        api_dict['request']['url'] = urlpath

    def _make_request_method(self, api_dict, method):
        """ parse method and make method of api request
        """
        if not method or method not in [
            "GET", "POST", "OPTIONS", "HEAD", "PUT", "PATCH", "DELETE", "CONNECT", "TRACE"]:
            logger.exception("method missed in request.")
            sys.exit(1)
        api_dict['request']['method'] = method

    def _make_request_headers(self, api_dict, method_value):
        """ parser consumes and make headers of api request
            Args:
                {
                    "post": {
                    "consumes": [
                        "application/json",
                    ],

            Return:
                {
                    "request":{
                        "headers":{
                            "Content-Type": "application/json"
                        }
                    }
                }
        """
        


















