
from loguru import logger

def load_swagger_api(file_path):
    """ load swagger api file and return swagger_all_info dict about swagger api file

        Args:
            file_path (str)

        Returns:
            all

    """
    with io.open(file_path, "r+", encoding="utf-8-sig") as f:
        try:
            content_json = json.loads(f.read())
            return content_json
        except (KeyError, TypeError):
            logging.error("swagger api file content error: {}".format(file_path))
            sys.exit(1)

def convert_x_www_form_urlencoded_to_dict(post_data):
    """ convert x_www_form_urlencoded data to dict

    Args:
        post_data (str): a=1&b=2

    Returns:
        dict: {"a":1, "b":2}

    """
    if isinstance(post_data, str):
        converted_dict = {}
        for k_v in post_data.split("&"):
            try:
                key, value = k_v.split("=")
            except ValueError:
                raise Exception(
                    "Invalid x_www_form_urlencoded data format: {}".format(post_data)
                )
            converted_dict[key] = unquote(value)
        return converted_dict
    else:
        return post_data

