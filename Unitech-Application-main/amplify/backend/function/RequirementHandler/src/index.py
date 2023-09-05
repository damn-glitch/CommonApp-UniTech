import json

import boto3


REQUIREMENT_FORMAT = {
    "RequirementName": str,
    "RequirementType": str,
    "RequirementAttributes": list,
}

REQUIREMENT_TYPES = {
    "STRING": {
        "valid_attributes": [
            "minlength",
            "maxlength",
            "regex",
        ],
    },
    "DOCUMENT": {
        "valid_attributes": [
            "minsize",
            "maxsize",
            "regex",
        ],
    },
    "OPTIONS": {
        "valid_attributes": [
            "STRING",
            "DOCUMENT",
            "POOL",
        ],
    },
    "POOL": {
        "valid_attributes": [
            "STRING",
            "DOCUMENT",
            "OPTIONS",
        ],
    },
}


def build_response(status_code: int, body, headers: dict = {}, **additional_kwargs) -> dict:
    return {
        "statusCode": status_code,
        "body": json.dumps(body),
        "headers": {
            "Content-Type": "application/json; charset=utf-8",
            "Access-Control-Allow-Origin": "*",
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            **headers,
        },
        **additional_kwargs,
    }


def get_dynamodb_table(table_name="RequirementInformation"):
    """Fetch the relevant DynamoDB table
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    except Exception:
        return
    return table


def validate_attributes(requirement_type: str, requirement_attributes: list):
    if requirement_type not in REQUIREMENT_TYPES:
        return build_response(
            status_code=500,
            body={"message": "Could not add requirement"}
        )
    for requirement_attribute in requirement_attributes:
        if requirement_attribute not in REQUIREMENT_TYPES[requirement_attribute]["valid_attributes"]:
            return None, build_response(
                status_code=400,
                body={
                    "message": f"Invalid parameter {requirement_attribute}"
                }
            )
    return True, ...


def string_handler(requirement_attributes: dict):
    result, response = validate_attributes(
        requirement_type="STRING",
        requirement_attributes=requirement_attributes.keys(),
    )
    if result is None:
        return None, response
    # TODO Check default ranges
    return requirement_attributes, ...


def document_handler(requirement_attributes):
    result, response = validate_attributes(
        requirement_type="DOCUMENT",
        requirement_attributes=requirement_attributes.keys(),
    )
    if result is None:
        return None, response
    # TODO Check default ranges
    return requirement_attributes, ...


def options_handler(requirement_attributes):
    result, response = validate_attributes(
        requirement_type="OPTIONS",
        requirement_attributes=requirement_attributes.keys(),
    )
    if result is None:
        return None, response
    # TODO Check default ranges
    return requirement_attributes, ...


def pool_handler(requirement_attributes):
    result, response = validate_attributes(
        requirement_type="POOL",
        requirement_attributes=requirement_attributes.keys(),
    )
    if result is None:
        return None, response
    # TODO Check default ranges
    return requirement_attributes, ...


REQUIREMENT_HANDLER = {
    "STRING": string_handler,
    "DOCUMENT": document_handler,
    "OPTIONS": options_handler,
    "POOL": pool_handler,
}


def create_requirement(requirement: dict):
    if requirement["RequirementType"] not in REQUIREMENT_HANDLER.keys():
        return build_response(
            status_code=400,
            body={"message": "Invalid requirement type specified"}
        )
    result, response = REQUIREMENT_HANDLER[requirement["RequirementType"]]()
    if result is None:
        return response
    try:
        requirement_table = get_dynamodb_table()
        requirement_table.put_item(
            Item=requirement
        )
    except Exception:
        return build_response(
            status_code=500,
            body={"message": "Could not add requirement"}
        )
    return build_response(
        status_code=201,
        body={"message": "Created the requirement"}
    )


def parse_body(body: dict):
    if body is None:
        return None, 404
    elif not isinstance(body, dict):
        try:
            body = json.loads(body)
        except json.decoder.JSONDecodeError:
            return None, 404
        except Exception:
            return None, 500
    for requirement_attribute in body.keys():
        if requirement_attribute not in REQUIREMENT_FORMAT:
            return None, 404
        elif not isinstance(body[requirement_attribute], REQUIREMENT_FORMAT[requirement_attribute]):
            return 400
    return body, 200


def requirement_handler(body: dict):
    requirement, code = parse_body(body)
    if requirement is None:
        return build_response(
            status_code=code,
            body={"message": "Invalid body provided"}
        )
    return create_requirement(requirement)


def handler(event, context):
    if not event.get('httpMethod', "") == "POST":
        return build_response(
            status_code=405,
            body={"message": "Method not allowed"}
        )
    return requirement_handler(event.get('body'))
