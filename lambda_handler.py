"""
AWS Lambda Handler for Otomoto Scraper

This module adapts the scraper to work with AWS Lambda.
Lambda invokes this handler function when triggered.
"""

import json
import os
from src.scraper.main import main as run_scraper


def handler(event, context):
    """
    AWS Lambda handler function.
    
    Lambda invokes this function when:
    - Manually triggered via AWS Console/CLI
    - EventBridge (CloudWatch Events) scheduled trigger
    - API Gateway (if configured)
    
    Args:
        event (dict): Lambda event data. For EventBridge schedule, contains:
            - time: ISO 8601 timestamp
            - detail-type: "Scheduled Event"
            - resources: ARN of the EventBridge rule
        
        context (LambdaContext): Lambda runtime information
            - request_id: Unique request ID
            - function_name: Name of Lambda function
            - memory_limit_in_mb: Allocated memory
            - invoked_function_arn: Function ARN
    
    Returns:
        dict: Response with statusCode and body
            - 200: Success
            - 500: Error occurred
    """
    print(f"Lambda invoked with event: {json.dumps(event)}")
    print(f"Request ID: {context.aws_request_id}")
    print(f"Function: {context.function_name}")
    print(f"Memory limit: {context.memory_limit_in_mb} MB")
    
    try:
        # Run the scraper
        print("Starting scraper...")
        run_scraper()
        
        # Check if output file was created
        output_file = "/tmp/data/all_offers.jsonl"
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"Scraper completed. Output file size: {file_size} bytes")
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Scraper completed successfully',
                    'output_file': output_file,
                    'file_size': file_size,
                    'request_id': context.aws_request_id
                })
            }
        else:
            print("Warning: Output file not found")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'Scraper completed but no output file found',
                    'request_id': context.aws_request_id
                })
            }
    
    except Exception as e:
        print(f"Error running scraper: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error running scraper',
                'error': str(e),
                'request_id': context.aws_request_id
            })
        }
