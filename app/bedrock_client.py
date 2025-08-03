import boto3
import json
import base64
import logging
from typing import Dict, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BedrockClient:
    def __init__(self):
        """Initialize the Bedrock client with AWS credentials."""
        try:
            # Check for required environment variables
            aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            
            if not aws_access_key or not aws_secret_key:
                raise ValueError("AWS credentials not found in environment variables")
            
            self.bedrock_runtime = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
            )
            self.model_id = "arn:aws:bedrock:us-east-2:905418105552:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0"
            
            # Test the connection
            logger.info("🔐 AWS Bedrock client initialized with credentials")
            logger.info(f"🌍 Region: {os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')}")
            logger.info(f"🤖 Model: Claude 3.5 Sonnet")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS Bedrock client: {str(e)}")
            raise
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string."""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image to base64: {str(e)}")
            raise
    
    def extract_invoice_data(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Extract structured data from invoice image using Claude 3.5 Vision.
        
        Args:
            image_path: Path to the invoice image
            prompt: Extraction prompt for Claude
            
        Returns:
            Dictionary containing extracted invoice data
        """
        try:
            # Encode image to base64
            logger.info(f"📸 Encoding image: {image_path}")
            image_base64 = self.encode_image_to_base64(image_path)
            logger.info(f"✅ Image encoded successfully (size: {len(image_base64)} characters)")
            
            # Determine image format
            image_format = "image/jpeg"
            if image_path.lower().endswith('.png'):
                image_format = "image/png"
            elif image_path.lower().endswith('.gif'):
                image_format = "image/gif"
            elif image_path.lower().endswith('.webp'):
                image_format = "image/webp"
            
            logger.info(f"🎨 Image format detected: {image_format}")
            
            # Prepare the request payload
            message = {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_format,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": [message],
                "temperature": 0.1,
                "system": "You are a professional invoice data extraction assistant. Always respond with valid JSON format."
            }
            
            logger.info(f"🚀 Calling AWS Bedrock Claude 3.5 Vision...")
            logger.info(f"📋 Prompt length: {len(prompt)} characters")
            
            # Make the API call
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            extracted_text = response_body['content'][0]['text']
            
            logger.info("✅ Successfully received response from Claude")
            logger.info(f"📄 Response length: {len(extracted_text)} characters")
            
            # Try to parse as JSON, if it fails return as text
            try:
                parsed_data = json.loads(extracted_text)
                logger.info("✅ Successfully parsed JSON response")
                parsed_data['extraction_successful'] = True
                parsed_data['extracted_by'] = 'AWS Bedrock Claude 3.5 Vision'
                return parsed_data
            except json.JSONDecodeError as json_error:
                logger.warning(f"⚠️ Response was not valid JSON: {str(json_error)}")
                logger.info(f"📝 Raw response: {extracted_text[:200]}...")
                # If Claude returns non-JSON text, wrap it in a structure
                return {
                    "raw_extraction": extracted_text,
                    "extraction_successful": False,
                    "error": "Response was not in valid JSON format",
                    "json_error": str(json_error),
                    "extracted_by": 'AWS Bedrock Claude 3.5 Vision'
                }
                
        except Exception as e:
            logger.error(f"❌ Error extracting invoice data: {str(e)}")
            logger.error(f"🔍 Error type: {type(e).__name__}")
            return {
                "error": str(e),
                "extraction_successful": False,
                "extracted_by": 'AWS Bedrock Claude 3.5 Vision (Failed)'
            }
    
    def chat_with_claude(self, question: str, context: str) -> str:
        """
        Chat with Claude using the invoice context for RAG.
        
        Args:
            question: User's question
            context: Invoice data context
            
        Returns:
            Claude's response
        """
        try:
            prompt = f"""
            Based on the following invoice data, please answer the user's question accurately and concisely.
            
            Invoice Data:
            {context}
            
            User Question: {question}
            
            Please provide a helpful and accurate answer based only on the information available in the invoice data.
            If the information is not available in the invoice, please say so clearly.
            """
            
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3
            }
            
            logger.info("Sending chat request to Claude...")
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error in chat with Claude: {str(e)}")
            return f"Sorry, I encountered an error while processing your question: {str(e)}"
