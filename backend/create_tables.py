import boto3
from botocore.exceptions import ClientError
from config import AWS_REGION, AWS_PROFILE, DYNAMODB_TABLES

def create_dynamodb_tables():
    session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
    dynamodb = session.resource('dynamodb')
    
    tables_config = [
        {
            'TableName': DYNAMODB_TABLES['clients'],
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': DYNAMODB_TABLES['recommendations'],
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'clientId', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'clientId-index',
                    'KeySchema': [
                        {'AttributeName': 'clientId', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': DYNAMODB_TABLES['alerts'],
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'clientId', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'clientId-index',
                    'KeySchema': [
                        {'AttributeName': 'clientId', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': DYNAMODB_TABLES['cron_jobs'],
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'},
                {'AttributeName': 'clientId', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'clientId-index',
                    'KeySchema': [
                        {'AttributeName': 'clientId', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'}
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': DYNAMODB_TABLES['analysis_results'],
            'KeySchema': [
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table_config in tables_config:
        try:
            table = dynamodb.create_table(**table_config)
            print(f"Creating table {table_config['TableName']}...")
            table.wait_until_exists()
            print(f"✓ Table {table_config['TableName']} created successfully!")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"✓ Table {table_config['TableName']} already exists")
            else:
                print(f"✗ Error creating table {table_config['TableName']}: {e}")

if __name__ == "__main__":
    print("Creating DynamoDB tables...")
    create_dynamodb_tables()
    print("\nAll tables created successfully!")
