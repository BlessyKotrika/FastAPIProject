# KhetiPulse AWS Deployment Guide

This guide provides comprehensive instructions for deploying the KhetiPulse application to AWS using ECS Fargate with a load balancer and automated CI/CD pipeline.

## 🏗️ Architecture Overview

The deployment consists of:
- **ECS Fargate**: Containerized application running on AWS Fargate
- **Application Load Balancer (ALB)**: Distributes traffic across ECS tasks
- **Amazon ECR**: Docker container registry
- **DynamoDB**: NoSQL database for user data and advisory history
- **S3**: Storage for data files
- **AWS Systems Manager (SSM)**: Secure parameter storage
- **GitHub Actions**: CI/CD pipeline for automated deployments

## 📋 Prerequisites

### AWS Account Setup
1. Create an AWS account or use an existing one
2. Install and configure AWS CLI:
   ```bash
   aws configure
   ```
3. Create an IAM user with the following permissions:
   - `AmazonEC2FullAccess`
   - `AmazonECS_FullAccess`
   - `AmazonECR_FullAccess`
   - `CloudWatchFullAccess`
   - `AWSCloudFormationFullAccess`
   - `AmazonSSMFullAccess`
   - `AmazonDynamoDBFullAccess`
   - `AmazonS3FullAccess`
   - `IAMFullAccess`

### GitHub Repository Setup
1. Fork or clone this repository to your GitHub account
2. Go to repository Settings → Secrets and variables → Actions
3. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key

### Required API Keys & Secrets
1. **OpenWeather API Key**: Get from [OpenWeather](https://openweathermap.org/api)
2. **Bedrock Knowledge Base ID**: From AWS Console after creation.
3. **Mandi API Key**: [Data.gov.in](https://data.gov.in/register)
4. **JWT Secret Key**: Any 32+ char secure string.

## 🚀 Quick Deployment

### Step 1: Infrastructure Setup
Run the automated setup script:

```bash
chmod +x setup-aws-infrastructure.sh
./setup-aws-infrastructure.sh
```

This script will:
- Create ECR repository
- Set up DynamoDB tables
- Create S3 bucket
- Configure SSM parameters
- Deploy CloudFormation stack with VPC, ECS, and ALB

### Step 2: Configure API Keys
Update the SSM parameters with your actual API keys:

```bash
# OpenWeather API Key
aws ssm put-parameter \
    --name "/khetipulse/prod/openweather-api-key" \
    --value "your-actual-openweather-api-key" \
    --type "SecureString" \
    --overwrite \
    --region us-east-1

# Bedrock Knowledge Base ID (optional)
aws ssm put-parameter \
    --name "/khetipulse/prod/bedrock-kb-id" \
    --value "your-bedrock-kb-id" \
    --type "String" \
    --overwrite \
    --region us-east-1
```

### Step 3: Initial Deployment
Push your code to trigger the first deployment:

```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

The GitHub Actions workflow will:
1. Run tests
2. Build Docker image
3. Push to ECR
4. Update ECS service

## 🔧 Manual Configuration

### CloudFormation Parameters
The `ecs-template.yaml` supports the following parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| VpcCidr | 10.0.0.0/16 | CIDR block for VPC |
| ContainerPort | 8000 | Port the container listens on |
| DesiredCount | 2 | Number of ECS tasks |
| EnvironmentName | prod | Environment name |

### Environment Variables
The application uses these environment variables:

| Variable | Description | Source |
|----------|-------------|--------|
| AWS_REGION | AWS region | CloudFormation |
| DYNAMODB_TABLE_USERS | Users table name | CloudFormation |
| DYNAMODB_TABLE_ADVISORY | Advisory table name | CloudFormation |
| S3_BUCKET_NAME | S3 bucket name | CloudFormation |
| SECRET_KEY | JWT secret key | SSM Parameter |
| OPENWEATHER_API_KEY | Weather API key | SSM Parameter |
| BEDROCK_KB_ID | Bedrock KB ID | SSM Parameter |
| CORS_ORIGINS | Allowed CORS origins | Config (default: *) |

## 🔍 Monitoring and Troubleshooting

### Check Application Logs
```bash
# Get ECS service logs
aws logs tail /ecs/khetipulse-ecs --follow --region us-east-1

# Check ECS service status
aws ecs describe-services \
    --cluster khetipulse-cluster \
    --services khetipulse-service \
    --region us-east-1
```

### Check Load Balancer Health
```bash
# Get ALB DNS name
aws cloudformation describe-stacks \
    --stack-name khetipulse-ecs \
    --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
    --output text \
    --region us-east-1

# Check target health
aws elbv2 describe-target-health \
    --target-group-arn $(aws elbv2 describe-target-groups \
        --names khetipulse-ecs-tg \
        --query 'TargetGroups[0].TargetGroupArn' \
        --output text) \
    --region us-east-1
```

### Common Issues

1. **Container fails to start**
   - Check CloudWatch logs for application errors
   - Verify environment variables are set correctly
   - Ensure DynamoDB tables exist

2. **Load balancer shows unhealthy targets**
   - Check health check endpoint `/`
   - Verify security groups allow traffic
   - Check ECS task network configuration

3. **CI/CD pipeline fails**
   - Verify AWS credentials in GitHub secrets
   - Check ECR repository exists
   - Ensure IAM permissions are correct

## 🔒 Security Considerations

### Network Security
- ECS tasks run in private subnets
- ALB accepts traffic from the internet (ports 80/443)
- Security groups restrict traffic between components

### Data Protection
- Sensitive data stored in SSM Parameter Store
- DynamoDB encryption enabled by default
- S3 bucket with appropriate access controls

### Access Control
- IAM roles with least privilege principle
- GitHub Actions uses temporary AWS credentials
- API authentication via JWT tokens

## 📊 Scaling

### Auto Scaling
The deployment includes CPU-based auto scaling:
- Scales out when CPU > 70%
- Scales in when CPU < 70%
- Minimum 2 tasks, maximum 10 tasks

### Manual Scaling
```bash
# Scale to 4 tasks
aws ecs update-service \
    --cluster khetipulse-cluster \
    --service khetipulse-service \
    --desired-count 4 \
    --region us-east-1
```

## 🌐 Custom Domain (Optional)

1. **Route 53 Hosted Zone**
   ```bash
   aws route53 create-hosted-zone \
       --name yourdomain.com \
       --caller-reference $(date +%s) \
       --region us-east-1
   ```

2. **SSL Certificate**
   ```bash
   aws acm request-certificate \
       --domain-name yourdomain.com \
       --validation-method DNS \
       --region us-east-1
   ```

3. **Update ALB Listener**
   Modify the CloudFormation template to add HTTPS listener and certificate.

## 🔄 Updates and Maintenance

### Application Updates
Push to the main branch to trigger automatic deployment.

### Infrastructure Updates
```bash
# Update CloudFormation stack
aws cloudformation update-stack \
    --stack-name khetipulse-ecs \
    --template-body file://ecs-template.yaml \
    --parameters ParameterKey=DesiredCount,ParameterValue=4 \
    --capabilities CAPABILITY_IAM \
    --region us-east-1
```

### Backup and Recovery
- DynamoDB continuous backups are enabled
- S3 versioning can be enabled for data protection
- CloudFormation stack can be recreated if needed

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Check GitHub Actions workflow logs
4. Consult AWS documentation

## 📋 Checklist

- [ ] AWS CLI configured
- [ ] GitHub secrets added
- [ ] API keys configured in SSM
- [ ] Infrastructure deployed
- [ ] First deployment successful
- [ ] Application accessible via ALB URL
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up (optional)

## 🎯 Cost Optimization

### Estimated Monthly Costs (us-east-1)
- ECS Fargate: $20-50 (2-4 tasks, 0.5 vCPU, 1GB RAM each)
- ALB: $20-30
- DynamoDB: $5-15 (on-demand pricing)
- S3: $1-5
- ECR: $1-2
- CloudWatch: $5-10

**Total: $50-110/month** (depending on usage)

### Cost Saving Tips
- Use reserved instances for consistent workloads
- Implement auto-scaling to reduce idle capacity
- Monitor and optimize DynamoDB read/write capacity
- Set up billing alerts