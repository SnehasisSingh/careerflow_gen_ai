
import json
import os

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "message": "CareerFlow AI API is running",
            "modules": ["CareerLens", "KnowFlow"],
            "table": os.environ["TABLE_NAME"]
        })
    }
