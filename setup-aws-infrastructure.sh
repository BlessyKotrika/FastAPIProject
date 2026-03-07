#!/bin/bash

# KhetiPulse AWS Infrastructure Setup Script
# This script sets up the complete AWS infrastructure for KhetiPulse

set -e

# Configuration
STACK_NAME="khetipulse-ecs"
REGION="us-east-1"
ENVIRONMENT="prod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting KhetiPulse AWS Infrastructure Setup${NC}"

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📍 Using AWS Region: ${REGION}${NC}"
echo -e "${YELLOW}📍 Stack Name: ${STACK_NAME}${NC}"

# Create ECR repository
echo -e "${GREEN}📦 Creating ECR Repository...${NC}"
if ! aws ecr describe-repositories --repository-names khetipulse-api --region $REGION &> /dev/null; then
    aws ecr create-repository \
        --repository-name khetipulse-api \
        --region $REGION \
        --image-scanning-configuration scanOnPush=true \
        --image-tag-mutability MUTABLE
    echo -e "${GREEN}✅ ECR Repository created${NC}"
else
    echo -e "${YELLOW}⚠️  ECR Repository already exists${NC}"
fi

# Create DynamoDB tables
echo -e "${GREEN}🗄️  Creating DynamoDB Tables...${NC}"

# Users table
if ! aws dynamodb describe-table --table-name Users --region $REGION &> /dev/null; then
    aws dynamodb create-table \
        --table-name Users \
        --attribute-definitions \
            AttributeName=user_id,AttributeType=S \
            AttributeName=username,AttributeType=S \
            AttributeName=email,AttributeType=S \
            AttributeName=google_id,AttributeType=S \
        --key-schema AttributeName=user_id,KeyType=HASH \
        --global-secondary-indexes \
            "[
                {
                    \"IndexName\": \"username-index\",
                    \"KeySchema\": [
                        {\"AttributeName\": \"username\", \"KeyType\": \"HASH\"}
                    ],
                    \"Projection\": {\"ProjectionType\": \"ALL\"},
                    \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
                },
                {
                    \"IndexName\": \"email-index\",
                    \"KeySchema\": [
                        {\"AttributeName\": \"email\", \"KeyType\": \"HASH\"}
                    ],
                    \"Projection\": {\"ProjectionType\": \"ALL\"},
                    \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
                },
                {
                    \"IndexName\": \"google_id-index\",
                    \"KeySchema\": [
                        {\"AttributeName\": \"google_id\", \"KeyType\": \"HASH\"}
                    ],
                    \"Projection\": {\"ProjectionType\": \"ALL\"},
                    \"ProvisionedThroughput\": {\"ReadCapacityUnits\": 5, \"WriteCapacityUnits\": 5}
                }
            ]" \
        --billing-mode PAY_PER_REQUEST \
        --region $REGION
    echo -e "${GREEN}✅ Users table created${NC}"
else
    echo -e "${YELLOW}⚠️  Users table already exists${NC}"
fi

# AdvisoryHistory table
if ! aws dynamodb describe-table --table-name AdvisoryHistory --region $REGION &> /dev/null; then
    aws dynamodb create-table \
        --table-name AdvisoryHistory \
        --attribute-definitions \
            AttributeName=user_id,AttributeType=S \
            AttributeName=timestamp,AttributeType=S \
        --key-schema \
            AttributeName=user_id,KeyType=HASH \
            AttributeName=timestamp,KeyType=RANGE \
        --billing-mode PAY_PER_REQUEST \
        --region $REGION
    echo -e "${GREEN}✅ AdvisoryHistory table created${NC}"
else
    echo -e "${YELLOW}⚠️  AdvisoryHistory table already exists${NC}"
fi

# Create S3 bucket
BUCKET_NAME="khetipulse-data-$(aws sts get-caller-identity --query Account --output text)-$REGION"
echo -e "${GREEN}🪣 Creating S3 Bucket: ${BUCKET_NAME}...${NC}"

if ! aws s3api head-bucket --bucket $BUCKET_NAME --region $REGION &> /dev/null; then
    aws s3api create-bucket \
        --bucket $BUCKET_NAME \
        --region $REGION \
        --create-bucket-configuration LocationConstraint=$REGION
    echo -e "${GREEN}✅ S3 bucket created${NC}"
else
    echo -e "${YELLOW}⚠️  S3 bucket already exists${NC}"
fi

# Create SSM parameters
echo -e "${GREEN}🔐 Creating SSM Parameters...${NC}"

# Generate a random secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create SSM parameters if they don't exist
if ! aws ssm get-parameter --name "/khetipulse/${ENVIRONMENT}/secret-key" --region $REGION &> /dev/null; then
    aws ssm put-parameter \
        --name "/khetipulse/${ENVIRONMENT}/secret-key" \
        --value "$SECRET_KEY" \
        --type "SecureString" \
        --region $REGION
    echo -e "${GREEN}✅ Secret key parameter created${NC}"
else
    echo -e "${YELLOW}⚠️  Secret key parameter already exists${NC}"
fi

if ! aws ssm get-parameter --name "/khetipulse/${ENVIRONMENT}/openweather-api-key" --region $REGION &> /dev/null; then
    aws ssm put-parameter \
        --name "/khetipulse/${ENVIRONMENT}/openweather-api-key" \
        --value "your-openweather-api-key-here" \
        --type "SecureString" \
        --region $REGION
    echo -e "${YELLOW}⚠️  OpenWeather API key parameter created with placeholder value. Please update it with your actual API key.${NC}"
else
    echo -e "${YELLOW}⚠️  OpenWeather API key parameter already exists${NC}"
fi

if ! aws ssm get-parameter --name "/khetipulse/${ENVIRONMENT}/bedrock-kb-id" --region $REGION &> /dev/null; then
    aws ssm put-parameter \
        --name "/khetipulse/${ENVIRONMENT}/bedrock-kb-id" \
        --value "" \
        --type "String" \
        --region $REGION
    echo -e "${YELLOW}⚠️  Bedrock KB ID parameter created with empty value. Please update it with your actual Knowledge Base ID.${NC}"
else
    echo -e "${YELLOW}⚠️  Bedrock KB ID parameter already exists${NC}"
fi

# Deploy CloudFormation stack
echo -e "${GREEN}☁️  Deploying CloudFormation Stack...${NC}"

aws cloudformation deploy \
    --template-file ecs-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        EnvironmentName=$ENVIRONMENT \
    --capabilities CAPABILITY_IAM \
    --region $REGION

echo -e "${GREEN}✅ CloudFormation stack deployed successfully!${NC}"

# Get stack outputs
LOAD_BALANCER_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
    --output text \
    --region $REGION)

LOAD_BALANCER_DNS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text \
    --region $REGION)

echo -e "${GREEN}🎉 Infrastructure setup complete!${NC}"
echo -e "${GREEN}📋 Summary:${NC}"
echo -e "   Load Balancer URL: ${LOAD_BALANCER_URL}"
echo -e "   Load Balancer DNS: ${LOAD_BALANCER_DNS}"
echo -e "   ECR Repository: $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${REGION}.amazonaws.com/khetipulse-api"
echo -e "   S3 Bucket: ${BUCKET_NAME}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo -e "   1. Update the OpenWeather API key in SSM Parameter Store"
echo -e "   2. Set up your Bedrock Knowledge Base and update the KB ID in SSM"
echo -e "   3. Push your Docker image to ECR"
echo -e "   4. Configure your domain name (optional)"
echo -e "   5. Set up monitoring and alerts (optional)"
echo ""
echo -e "${GREEN}🚀 Ready for deployment!${NC}"