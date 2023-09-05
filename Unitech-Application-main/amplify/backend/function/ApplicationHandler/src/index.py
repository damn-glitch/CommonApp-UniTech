import json

import boto3

APPLICATION_ATTRIBUTES = {
    "SelectedUniversities": list,
    "ApplicantValues": dict,
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
            ** headers,
        },
        **additional_kwargs,
    }


def get_user_id(requestContext: dict):
    if requestContext is None:
        return None
    return requestContext.get('identity', {}).get('cognitoIdentityId')


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
    for attribute in body.keys():
        if attribute not in APPLICATION_ATTRIBUTES:
            print(f"{attribute} is not a valid attribute")
            return None, 400
        elif not isinstance(body[attribute], APPLICATION_ATTRIBUTES[attribute]):
            print(
                f"{attribute} is not a type {APPLICATION_ATTRIBUTES[attribute]}"
            )
            return None, 400
    return body, ...  # No return code required


def get_dynamodb_table(table_name="ApplicationInformation"):
    """Fetch the relevant DynamoDB table
    """
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
    except Exception:
        return
    return table


def create_application(application: dict):
    """Add the application to the DynamoDB table
    """
    application_table = get_dynamodb_table(
        table_name="ApplicationInformation",
    )
    if application_table is None:
        return build_response(
            status_code=500,
            body={"message": "Could not add application"}
        )
    try:
        application_table.put_item(
            Item=application
        )
    except Exception:
        return build_response(
            status_code=500,
            body={"message": "Could not add application"}
        )
    return build_response(
        status_code=201,
        body={"message": "Created the application"}
    )


def application_handler(requestContext: dict, body: dict) -> dict:
    """Manages the process of adding an application 
    """
    if (user_id := get_user_id(requestContext)) is None:
        return build_response(
            status_code=401,
            body={"message": "No credentials supplied"}
        )
    body, code = parse_body(body)
    if body is None:
        return build_response(
            status_code=code,
            body={"message": "Invalid body"}
        )
    application = {
        "ApplicantUserID": user_id,
        **body,
    }
    return create_application(
        application
    )


def handler(event, context):
    print("[i] Received event")
    if event.get("httpMethod") and event.get("httpMethod") == "POST":
        return application_handler(
            requestContext=event.get("requestContext"),
            body=event.get("body"),
        )
    return build_response(
        status_code=405,
        body={"message": "Method not allowed"}
    )
