from swagger2case import utils
import re
from loguru import logger
import sys
import json

class SwaggerParser(object):

    def __init__(self, swagger_file_path, filter_str=None, exclude_str=None):
        self.swagger_file_path = swagger_file_path
        self.filter_str = filter_str
        self.exclude_str = exclude_str or ""
        self.swagger_all_info = utils.load_swagger_api(swagger_file_path)

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
        paths_dict = self.swagger_all_info['paths']
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
            "request": {
                'url': '',
                'method': '',
                'headers': {},
                'data': {},
                'json': {},
                'params': {}
            },
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
        if method_value['operationId']:
            api_dict['name'] = method_value['operationId']
        else:
            logger.exception("operationId missed in swagger api file")

    def _prepare_baseurl(self, api_dict):
        """
        parser host/basePath/schemes info and make base_url of api
        """
        host = self.swagger_all_info['host']
        basepath = self.swagger_all_info['basePath']
        schemes = self.swagger_all_info['schemes'][0]
        if host and basepath and schemes:
            api_dict['base_url'] = f"{schemes}:{host}{basepath}"
        else:
            logger.exception("host or basePath or schemes miss in swagger api file")

    def _prepare_variables(self, api_dict, method_value):
        pass

    def _prepare_validate(self, api_dict, method_value):
        """ extract info from responses and make validate

            Arg:
                "responses": {
                    "200": {
                      "description": "successful operation",
                      "schema": {
                        "type": "array",
                        "items": {
                          "$ref": "#/definitions/Pet"
                        }
                      }
                    },
                    "400": {
                      "description": "Invalid tag value"
                    }
                },

            Return:

                "validate": [
                    {"eq": ["status_code", 200]},
                    {"eq": ["content.token", 16]}
                ]

        """
        if not utils.is_key_in_dict(r'responses', method_value):
            logger.exception("responses miss in swagger json file")
        else:
            for status_code_key, status_code_value in method_value['responses'].items():
                if utils.is_key_in_dict(r'[0-9]+', method_value['responses']):
                    api_dict['validate'].append(
                        {"eq": ["status_code", status_code_key]})
                    self._make_response_content(api_dict, status_code_value)
                elif utils.is_key_in_dict('default', method_value['responses']):
                    self._make_response_content(api_dict, status_code_value)
                else:
                    logger.info("responses is empty")
        self._make_response_headers(api_dict, method_value)

    def _make_response_content(self, api_dict, status_code_value):
        if utils.is_key_in_dict('description', status_code_value):
            api_dict['validate'].append(
                {"eq": ["content.description", status_code_value['description']]})

        if utils.is_key_in_dict('schema', status_code_value):
            self._make_response_schema_content(api_dict, status_code_value['schema'])

        if utils.is_key_in_dict('headers', status_code_value):
            for key, value in status_code_value['headers'].items():
                api_dict['validate'].append(
                    {"eq": [f'headers.{key}', utils.type_mapping.get(value['type'])]}
                )
    def _make_response_schema_content(self, api_dict, status_code_value_schema):
        if self._is_items_in_schema(status_code_value_schema):
            tag_name = status_code_value_schema['items']['$ref'].split('/')[-1]
            self._generate_response_content_with_tag_value(
                api_dict,
                tag_name)

        elif self._is_ref_in_schema(status_code_value_schema):

            tag_name = status_code_value_schema['$ref'].split('/')[-1]
            self._generate_response_content_with_tag_value(
                api_dict,
                tag_name)
        else:
            ### TODO: make compatible with more mimeType
            pass

    def _generate_response_content_with_tag_value(self, api_dict, tag_name):

        definitions_dict = utils.get_related_tag_definitions_content(
            self.swagger_all_info, tag_name)
        logger.info(f"definitions_dict_json::{definitions_dict}")
        api_dict['validate'].extend(utils.generate_validate_content_with_definitions(definitions_dict))

    def _is_items_in_schema(self, schema_dict):
        return utils.is_key_in_dict("items", schema_dict) and \
                utils.is_key_in_dict(r"\$ref", schema_dict['items'])

    def _is_ref_in_schema(self, schema_dict):
        return utils.is_key_in_dict(r"\$ref", schema_dict)


    def _make_response_headers(self, api_dict, method_value):
        if "produces" not in method_value:
            logger.exception("produces miss in swagger api file")
        if method_value['produces']:
            api_dict['validate'].append(
                {"eq": ['headers.Content-Type', method_value['produces'][0]]}
            )

    def _prepare_request(self, api_dict, method, method_value, urlpath):
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
                    }
                },
        """
        #logger.error(api_dict)
        self._make_request_url(api_dict, method, method_value, urlpath)
        self._make_request_method(api_dict, method)
        self._make_request_headers(api_dict, method_value)
        self._make_request_data(api_dict, method, method_value)

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
        if not urlpath:
            logger.error("urlpath missed in request.")
        elif re.search(r'\{(.*)\}', urlpath):
            new_nurlpath = re.sub(r'\{(.*)\}', "$\\1", urlpath)

            api_dict['variables'].update({re.search(r'\{(.*)\}', urlpath).group(1): ""})
            api_dict['request']['url'] = new_nurlpath
        elif method == 'get' and 'parameters' in method_value:
            params = {}
            for paramter in method_value['parameters']:
                paramter_key = paramter['name']
                params.update({paramter_key: ""})
            api_dict['request']['params'] = params
            api_dict['request']['url'] = urlpath
        else:
            api_dict['request']['url'] = urlpath

    def _make_request_method(self, api_dict, method):
        """ parse method and make method of api request
        """
        method = method.upper()
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
        if "consumes" in method_value:
            api_dict['request']['headers'].update({"Content-Type": method_value['consumes'][0]})

    def _make_request_data(self, api_dict, method, method_value):
        """ extract info from method value dict and make data of request.

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
                        }
                    },
                    "definitions": {
                        "Pet": {
                            "type": "object",
                            "required": [
                                "name",
                                "photoUrls"
                            ],
                            "properties": {
                                "id": {
                                  "type": "integer",
                                  "format": "int64"
                                },
                                "category": {
                                  "$ref": "#/definitions/Category"
                                },
                                "name": {
                                  "type": "string",
                                  "example": "doggie"
                                },
                                "photoUrls": {
                                  "type": "array",
                                  "xml": {
                                    "name": "photoUrl",
                                    "wrapped": true
                                  },
                                  "items": {
                                    "type": "string"
                                  }
                                },
                                "tags": {
                                  "type": "array",
                                  "xml": {
                                    "name": "tag",
                                    "wrapped": true
                                  },
                                  "items": {
                                    "$ref": "#/definitions/Tag"
                                  }
                                },
                                "status": {
                                  "type": "string",
                                  "description": "pet status in the store",
                                  "enum": [
                                    "available",
                                    "pending",
                                    "sold"
                                  ]
                                }
                            },
                              "xml": {
                                "name": "Pet"
                              }
                        },
                Return:
                    {
                        "request": {
                            "method": "POST",
                            "data": {"id": "", "name": ""}
                        }
                    }
        """
        if method not in ["post", "put", "patch", "delete"]:
            return api_dict

        mimeType = method_value.get('consumes', [''])[0]
        postdata = {}
        for parameter in method_value['parameters']:
            if "body" == parameter['in'] and "schema" in parameter:
                self._make_request_schema_data(postdata, parameter['schema'])
            if "formData" == parameter['in']:
                postdata.update({parameter['name']: ""})
            if "header" == parameter['in']:
                api_dict['variables'].update({parameter['name']: ""})
                api_dict['request']['headers'].update({parameter['name']: f"${parameter['name']}"})
        request_data_key = self._get_request_data_key(mimeType)
        logger.exception(postdata)
        api_dict["request"][request_data_key] = postdata

    def _make_request_schema_data(self, postdata, parameter_schema):
        if self._is_items_in_schema(parameter_schema):
            tag_name = parameter_schema['items']['$ref'].split('/')[-1]
            postdata.update(utils.get_related_tag_definitions_content(
                self.swagger_all_info,
                tag_name)
            )

        elif self._is_ref_in_schema(parameter_schema):

            tag_name = parameter_schema['$ref'].split('/')[-1]
            postdata.update(utils.get_related_tag_definitions_content(
                self.swagger_all_info,
                tag_name)
            )

        else:
            ### TODO: make compatible with more mimeType
            pass

    def _get_request_data_key(self, mimeType):
        request_data_key = "data"

        if not mimeType:
            return request_data_key

        if mimeType.startswith("application/json"):
            return "json"

        ## TODO: make compatible with more mimeType

        return request_data_key























