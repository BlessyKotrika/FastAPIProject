import boto3
from contextlib import contextmanager
from app.config import settings
from botocore.exceptions import ClientError

class DynamoDBUserTable:
    """Wrapper for DynamoDB users table operations."""
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_REGION)
        self.table = self.dynamodb.Table(settings.DYNAMODB_TABLE_USERS)
    
    def get_item(self, user_id: str):
        """Get user by user_id (primary key)."""
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None
    
    def get_item_by_username(self, username: str):
        """Get user by username using index."""
        try:
            response = self.table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            print(f"Error querying by username: {e}")
            return None
    
    def put_item(self, user_data: dict):
        """Insert or update a user."""
        try:
            self.table.put_item(Item=user_data)
            return True
        except ClientError as e:
            print(f"Error putting item: {e}")
            return False

def init_db():
    """Initialize DynamoDB table (table should be created in AWS console or via terraform)."""
    # Note: In production, use AWS CloudFormation or Terraform to manage table creation
    # This function serves as a placeholder for any initialization logic
    pass

@contextmanager
def get_db():
    """Provides a DynamoDB table resource."""
    db = DynamoDBUserTable()
    try:
        yield db
    except Exception as e:
        print(f"Error in database context: {e}")
        raise

# Initialize on module load
init_db()
