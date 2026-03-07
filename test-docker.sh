#!/bin/bash

# KhetiPulse Docker Build and Test Script

set -e

IMAGE_NAME="khetipulse-api"
TAG="latest"

echo "🏗️  Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

echo "🧪 Testing Docker image..."

# Run the container in the background
echo "🚀 Starting container..."
CONTAINER_ID=$(docker run -d -p 8000:8000 \
    -e SECRET_KEY="test-secret-key" \
    -e AWS_REGION="us-east-1" \
    -e DYNAMODB_TABLE_USERS="Users" \
    -e DYNAMODB_TABLE_ADVISORY="AdvisoryHistory" \
    -e S3_BUCKET_NAME="test-bucket" \
    -e OPENWEATHER_API_KEY="test-key" \
    -e AGMARKNET_API_KEY="test-key" \
    $IMAGE_NAME:$TAG)

echo "⏳ Waiting for container to be healthy..."
sleep 30

# Test health endpoint
echo "🏥 Testing health endpoint..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)

if [ "$HEALTH_STATUS" -eq 200 ]; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed with status: $HEALTH_STATUS"
    docker logs $CONTAINER_ID
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    exit 1
fi

# Test API docs endpoint
echo "📚 Testing API docs endpoint..."
DOCS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)

if [ "$DOCS_STATUS" -eq 200 ]; then
    echo "✅ API docs accessible!"
else
    echo "❌ API docs failed with status: $DOCS_STATUS"
fi

# Clean up
echo "🧹 Cleaning up..."
docker stop $CONTAINER_ID
docker rm $CONTAINER_ID

echo "🎉 Docker image test completed successfully!"
echo ""
echo "To run the container locally:"
echo "docker run -p 8000:8000 \\"
echo "  -e SECRET_KEY=\"your-secret-key\" \\"
echo "  -e AWS_REGION=\"us-east-1\" \\"
echo "  -e DYNAMODB_TABLE_USERS=\"Users\" \\"
echo "  -e DYNAMODB_TABLE_ADVISORY=\"AdvisoryHistory\" \\"
echo "  -e S3_BUCKET_NAME=\"your-bucket\" \\"
echo "  -e OPENWEATHER_API_KEY=\"your-api-key\" \\"
echo "  -e AGMARKNET_API_KEY=\"your-api-key\" \\"
echo "  $IMAGE_NAME:$TAG"