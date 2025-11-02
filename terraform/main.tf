terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-south-1"
  profile = "sova-profile"
}

# Generate a unique bucket name using timestamp
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket
resource "aws_s3_bucket" "stack_bucket" {
  bucket = "sova-stack-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "Stack Bucket"
    Environment = "Dev"
  }
}

# S3 Bucket Public Access Block Configuration (disable to allow public access)
resource "aws_s3_bucket_public_access_block" "stack_bucket_public_access" {
  bucket = aws_s3_bucket.stack_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 Bucket Policy for Public Read Access
resource "aws_s3_bucket_policy" "stack_bucket_policy" {
  bucket = aws_s3_bucket.stack_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.stack_bucket.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.stack_bucket_public_access]
}

# Upload stack.yml to S3
resource "aws_s3_object" "stack_yml" {
  bucket             = aws_s3_bucket.stack_bucket.id
  key                = "stack.yaml"
  source             = "${path.module}/stack.yaml"
  content_type       = "text/plain; charset=utf-8"
  content_disposition = "inline"

  etag = filemd5("${path.module}/stack.yaml")

  depends_on = [aws_s3_bucket_policy.stack_bucket_policy]
}

# Outputs
output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.stack_bucket.bucket
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.stack_bucket.arn
}

output "stack_yml_url" {
  description = "Public URL of the stack.yml file"
  value       = "https://${aws_s3_bucket.stack_bucket.bucket}.s3.ap-south-1.amazonaws.com/stack.yaml"
}

output "stack_yml_s3_uri" {
  description = "S3 URI of the stack.yml file"
  value       = "s3://${aws_s3_bucket.stack_bucket.bucket}/stack.yaml"
}
