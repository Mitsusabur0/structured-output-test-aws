import boto3
import json
from pathlib import Path
from schema import extraction_schema


USER_INPUT = "Busco depa en santiago con dos dormitorios"



# MODEL_ID = "qwen.qwen3-32b-v1:0"
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"


# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1' 
)

system_prompt = [{"text": "Tu trabajo es extraer filtros de búsqueda de un user_input, para un portal "
                  "chileno de venta de propiedades."}]


# Make the request with structured outputs
response = bedrock_runtime.converse(
    modelId=MODEL_ID,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": f"Mensaje del cliente: {USER_INPUT}"
                }
            ]
        },
    ],
    
    inferenceConfig={
        "maxTokens": 1024,
        "temperature": 0,
    },
    outputConfig={
        "textFormat": {
            "type": "json_schema",
            "structure": {
                "jsonSchema": {
                    "schema": json.dumps(extraction_schema),
                    "name": "lead_extraction",
                    "description": "Extract lead information from customer emails"
                }
            }
        }
    }
)


# Parse the schema-compliant JSON response
result = json.loads(response["output"]["message"]["content"][0]["text"])
print(json.dumps(result, indent=2))
