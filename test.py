import boto3
import json
from pathlib import Path
from schema import extraction_schema


USER_INPUT = "Elimina todos los filtros anteriores. Quiero departamentos en providencia."






# MODEL_ID = "google.gemma-3-12b-it"
# MODEL_ID = "openai.gpt-oss-120b-1:0"
# MODEL_ID = "qwen.qwen3-32b-v1:0"
MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"



# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1' 
)

system_prompt = [{"text": "Tu trabajo es extraer filtros de búsqueda para una página "
                  "chilena de venta de propiedades. Debes unir los filtros actuales con los " 
                  "del usuario. Los filtros del usuario tienen prioridad por sobre los actuales, "
                  "pero si el usuario no especifica un filtro que ya estaba presente, este debe mantenerse."}]


CURRENT_FILTERS_PATH = Path(__file__).with_name("current_filters.json")


# IN HERE -> INSERT A FUNCTION THAT READS THE FILE WITH CURRENT FILTERS
def read_current_filters():
    if not CURRENT_FILTERS_PATH.exists():
        return {}

    raw_content = CURRENT_FILTERS_PATH.read_text(encoding="utf-8").strip()
    if not raw_content:
        return {}

    return json.loads(raw_content)

filtros_actuales = read_current_filters()

# Make the request with structured outputs
response = bedrock_runtime.converse(
    modelId=MODEL_ID,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": f"Los filtros actuales son: {filtros_actuales}. "
                    f"Mensaje del cliente: {USER_INPUT}"
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

# IN HERE -> INSERT A FUNCTION THAT WRITES TO THE FILE WITH CURRENT FILTERS
def write_current_filters(result):
    CURRENT_FILTERS_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


write_current_filters(result)



print(json.dumps(result, indent=2))
