import boto3
import json


# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1' 
)
# Define your JSON schema

extraction_schema = {
    "type": "object",
    "properties": {
        "tipo_inmueble": {
            "type": "string",
            "description": "SOLO 'casa' o 'departamento'. No incluir si no se menciona o no está en los filtros actuales."
        },
        "comuna": {
            "type": "string",
            "description": "Nombre de la comuna en Chile (ej. 'Las Condes', 'Santiago')"
        },
        "dormitorios": {
            "type": "integer",
            "description": "Cantidad de dormitorios. Puede ser un número exacto o un arreglo [min, max]"
        },
        "banos": {
            "type": "integer",
            "description": "Cantidad de baños. Puede ser un número exacto o un arreglo [min, max]"
        },
        "precio": {
            "type": "number",
            "description": "Valor mínimo o exacto del precio"
        },
    },
    "required": [],
    "additionalProperties": False
}


# Make the request with structured outputs
response = bedrock_runtime.converse(
    modelId="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "ksa en FLORIDA, 3 baños, 2 dormitorios, precio maximo 2000 UF",
                }
            ]
        }
    ],
    inferenceConfig={
        "maxTokens": 1024
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
# result = json.loads(response["output"]["message"]["content"][0]["text"])
# result = json.loads(response)
# print(json.dumps(result, indent=2))
print(response)