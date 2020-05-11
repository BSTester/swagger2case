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
        for status_code, value in method_value['responses'].items():
            api_dict['validate'].append(
                {"eq": ["status_code", status_code]})

            self._make_response_headers(api_dict, method_value)

            if "schema" in value and "$ref" in value["schema"]["items"]:
                definitions_dict = self._get_definitions_ref_value(value["schema"]["items"]["$ref"])

                if "application/json" in method_value['produces']:
                    try:
                        definitions_dict_json = json.loads(definitions_dict)
                    except JSONDecodeError:
                        logger.warning(
                            "response definitions_dict can not be loaded as json: {}".format(definitions_dict)
                        )
                        return
                    if not isinstance(definitions_dict_json, dict):
                        return
                    logger.info(f"definitions_dict_json::{definitions_dict_json}")
                    for key, definitions_value in definitions_dict_json.items():
                        if isinstance(definitions_value, (dict, list)):
                            continue
                        api_dict['validate'].append(
                            {"eq": [f"content.{key}", definitions_value]})


    def _make_response_headers(self, api_dict, method_value):
        if "produces" in method_value:

            if "application/json" in method_value['produces']:
                api_dict['validate'].append(
                    {"eq": ["headers.Content-Type", "application/json"]}
                )
            elif "application/xml" in method_value['produces']:
                api_dict['validate'].append(
                    {"eq": ["headers.Content-Type", "application/xml"]}
                )
        else:
            logger.exception("produces miss in swagger api file")


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

        #logger.error(api_dict)
        if urlpath:
            result = re.search(r'\{(.*)\}', urlpath)
            if result:
                new_nurlpath = re.sub(r'\{(.*)\}', "$\\1", urlpath)

                api_dict['variables'].update({result.group(1): ""})
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
        else:
            logger.error("urlpath missed in request.")

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
        if method in ["post", "put", "patch", "delete"]:
            mimeType = method_value.get('consumes', [''])[0]
            postdata = {}

            for parameter in method_value['parameters']:
                if "body" == parameter['in'] and "schema" in parameter:
                    postdata.update(utils.get_related_tag_definitions_content(
                        self.swagger_all_info,
                        parameter['schema']['$ref'].split('/')[2])
                    )

                if "formData" == parameter['in']:
                    postdata.update({parameter['name']: ""})
                if "header" == parameter['in']:
                    api_dict['variables'].update({parameter['name']: ""})
                    api_dict['request']['headers'].update({parameter['name']: f"${parameter['name']}"})

            request_data_key = "data"
            if not mimeType:
                pass
            elif mimeType.startswith("application/json"):
                request_data_key = "json"
            else:
                # TODO: make compatible with more mimeType
                pass
            api_dict["request"][request_data_key] = postdata























