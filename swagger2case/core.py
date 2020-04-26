from har2case import utils

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






    def _make_apis(self):
        """ make api list.
            api list are parsed from swagger paths dict.

        """
        def is_exclude(url, exclude_str):
            exclude_str_list = exclude_str.split("|")
            for exclude_str in exclude_str_list:
                if exclude_str and exclude_str in url:
                    return True

            return False

        api_list = []
        swagger_all_info = load_swagger_api(self.swagger_file_path)
        host = swagger_all_info['host']
        basepath = swagger_all_info['basePath']
        paths_dict = swagger_all_info['paths']
        for key, value in paths_dict:

            if self.filter_str and self.filter_str not in key:
                continue

            if is_exclude(key, self.exclude_str):
                continue

            else:
                api_dict = _make_api(key, value, host, basepath)
                api_list.append(api_dict)
        return api_list

    def _make_api(self, url_path, value, host, basepath):
        """ extract info from path dict and make api

                Args:
                    "/pet": {
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
        self._prepare_name(api_dict, value)
        self._prepare_variables(api_dict, value, basepath, host)
        self._prepare_request(api_dict, url_path, value)
        self._prepare_validate(api_dict, value)
        return api_dict

    def _prepare_name(self, api_dict, value):
        '''
        parser operationId info from path dict and make name of api
        '''
        api_dict['name'] = value['operationId']

    def _prepare_variables(self, api_dict, value):
        pass

    def _prepare_validate(self, api_dict, value):
        pass

    def _prepare_request(self,api_dict, url_path, value):
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

        _make_request_url(api_dict, url_path, value)
        _make_request_method(api_dict, value)
        _make_request_headers(api_dict, value)
        _make_request_data(api_dict, value)

    def __make_request_url(self, api_dict, url_path, value):
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
                Returns:
                    {
                        "request": {
                            url: "/pet/findByStatus",
                            params: {"name": "sold"}
                        }
                    }

        """














