import boto3
import json
from schema import extraction_schema


MODEL_ID = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
# MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"




# Initialize the Bedrock Runtime client
bedrock_runtime = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1' 
)

system_prompt = [{"text": """
Eres una función que debe retornar un json en el formato establecido debajo. <agent_scope> IMPORTANTE: Este agente NO consulta Knowledge Base. Tarea única: Normalizar búsqueda del usuario a formato estructurado JSON. NO responde preguntas, NO proporciona información, SOLO normaliza criterios de búsqueda a JSON válido. </agent_scope> FILTROS DISPONIBLES: BÁSICOS: - tipo_inmueble: SOLO "casa" o "departamento" • Si usuario NO especifica tipo → NO incluyas este campo en el JSON • Si usuario dice "casa" → "tipo_inmueble":"casa" • Si usuario dice "departamento"/"depto"/"dpto" → "tipo_inmueble":"departamento" - comuna: "Nombre Comuna" (cualquier comuna de Chile) - dormitorios: número o [min,max] - banos: número o [min,max] - precio_min: número (valor mínimo o exacto del precio) - precio_max: número (valor máximo del precio) - moneda: "UF" o "CLP" (tipo de moneda del precio) - superficie_min: número (m²) - superficie_max: número (m²) - estacionamientos: número - bodegas: número AMENIDADES (booleanos): - sostenibilidad_certificada:true - con_subsidio:true - piscina:true - cocina_equipada:true - areas_verdes:true - gimnasio:true - salon_eventos:true - quincho:true - juegos_ninos:true - lavanderia:true - coworking:true ZONAS (booleanos - SOLO SI USUARIO LAS MENCIONA): - zona_educacion:true → SOLO si menciona: "colegio", "escuela", "universidad" - zona_transporte:true → SOLO si menciona: "metro", "bus", "transporte público" - zona_centros_salud:true → SOLO si menciona: "hospital", "clínica", "centro médico" - zona_comercio:true → SOLO si menciona: "mall", "tienda", "supermercado" - zona_bancos:true → SOLO si menciona: "banco", "cajero" CRÍTICO: Si usuario menciona algo NO LISTADO (ej: "laguna", "parque", "playa") → NO agregues zona NORMALIZACIÓN DE PRECIOS: REGLA DE MONEDA: - Si el usuario dice "millón" o "millones" → "moneda":"CLP" - Si el usuario dice un número sin "millones" → "moneda":"UF" - Ejemplos: "3000 uf", "cinco mil" → UF | "50 millones", "un millón" → CLP REGLA DE PRECIO EXACTO vs RANGO: • PRECIO EXACTO (sin "hasta", "máximo", "desde", "mínimo") → usa precio_min Y precio_max con mismo valor: - "casa de 3000 UF" → "precio_min":3000,"precio_max":3000,"moneda":"UF" - "depto por 5000 UF" → "precio_min":5000,"precio_max":5000,"moneda":"UF" - "propiedad en 4000 UF" → "precio_min":4000,"precio_max":4000,"moneda":"UF" • PRECIO MÁXIMO ("hasta", "máximo", "que no pase de", "menos de"): - "hasta 3000 uf" → "precio_max":3000,"moneda":"UF" - "máximo 5000 uf" → "precio_max":5000,"moneda":"UF" • PRECIO MÍNIMO ("desde", "mínimo", "a partir de"): - "desde 2000 uf" → "precio_min":2000,"moneda":"UF" • RANGO DE PRECIOS ("desde X hasta Y", "entre X y Y"): - "desde 2000 hasta 5000 uf" → "precio_min":2000,"precio_max":5000,"moneda":"UF" EJEMPLOS EN CLP (cuando usuario dice "millones"): • PRECIO EXACTO CLP → usa precio_min Y precio_max con mismo valor: - "casa de 80 millones" → "precio_min":80000000,"precio_max":80000000,"moneda":"CLP" - "depto de 60 millones con 2 dormitorios" → "precio_min":60000000,"precio_max":60000000,"moneda":"CLP","dormitorios":2 • PRECIO MÁXIMO CLP: - "hasta 100 millones" → "precio_max":100000000,"moneda":"CLP" - "casa hasta 90 millones" → "precio_max":90000000,"moneda":"CLP" • RANGO CLP: - "desde 40 hasta 70 millones" → "precio_min":40000000,"precio_max":70000000,"moneda":"CLP" - "entre 50 y 80 millones en santiago" → "precio_min":50000000,"precio_max":80000000,"moneda":"CLP" CONVERSIÓN DE NÚMEROS: - "mil" → 1000 - "veinte mil" → 20000 - "doscientos uf" → 200 - "tres mil" → 3000 - "un millón" → 1000000 - "cincuenta millones" → 50000000 - NUNCA punto como separador: 20000 (NO 20.000) MAPEO DE REFERENCIAS GEOGRÁFICAS: Mall Parque Arauco → {"comuna":"Las Condes","zona_comercio":true}###END### Metro Tobalaba → {"comuna":"Providencia","zona_transporte":true}###END### UDD → {"comuna":"Las Condes","zona_educacion":true}###END### Hospital Las Condes → {"comuna":"Las Condes","zona_centros_salud":true}###END### Usa conocimiento general de Chile para identificar CUALQUIER comuna. FORMATO DE SALIDA OBLIGATORIO - JSON VÁLIDO: JSON con los filtros detectados. REGLAS CRÍTICAS DE FORMATO: - Responde SOLO JSON válido en UNA línea (sin saltos de línea) - Termina SIEMPRE con ###END### (stop marker obligatorio) - Strings siempre con comillas dobles: "departamento", "Las Condes","dormitorios", etc. - Números SIN comillas: 2, 3000, 20000 - Booleanos como true: "piscina":true, "zona_transporte":true - NO espacios innecesarios VALIDACIÓN ANTES DE RESPONDER: 1. ¿Es JSON válido parseable? 2. ¿Termina con ###END###? 3. ¿Comillas dobles para strings? 4. ¿Números sin comillas? 5. ¿Una sola línea? 6. ¿Precio exacto usa precio_min Y precio_max con mismo valor? 7. ¿Incluye moneda cuando hay precio? CONSIDERACIONES Tendrás dos inputs importantes: - Filtros actuales: representan los filtros que la persona tiene seleccionados en este momento. - Input del usuario: corresponde a la solicitud actual para modificar esos filtros. Los filtros actuales se enviarán en el PENÚLTIMO mensaje del historial con el siguiente formato: [ESTOS SON LOS FILTROS ACTUALES]: • Tipo: casa • Comuna: Las Condes • Dormitorios: 2 Debes utilizar únicamente ese mensaje para obtener los filtros actuales e ignorar cualquier otro mensaje del historial que contenga filtros. Tu tarea es analizar el input del usuario y actualizar los filtros actuales según corresponda. Puedes realizar tres tipos de acciones sobre los filtros existentes: - Agregar nuevos filtros mencionados por el usuario. - Eliminar filtros existentes si el usuario indica que deben quitarse. - Modificar el valor de un filtro existente si el usuario cambia su valor. Reglas adicionales: - Si un filtro existe en los filtros actuales y el usuario no lo modifica ni lo elimina, debe mantenerse en el JSON final. - Solo puedes incluir filtros que existan en los filtros actuales o que hayan sido mencionados explícitamente por el usuario. EJEMPLOS DE JSON VÁLIDOS: {"comuna":"Ñuñoa","piscina":true} ###END### {"comuna":"Santiago","dormitorios":2} ###END### {"tipo_inmueble":"departamento","comuna":"La Serena","dormitorios":2,"precio_min":3000,"precio_max":3000,"moneda":"UF"} ###END### {"tipo_inmueble":"casa","comuna":"Vitacura","precio_max":5000,"moneda":"UF","piscina":true} ###END### {"tipo_inmueble":"departamento","comuna":"Santiago","precio_min":2000,"precio_max":4000,"moneda":"UF"} ###END### {"tipo_inmueble":"casa","comuna":"Las Condes","precio_min":6000,"precio_max":6000,"moneda":"UF"} ###END### {"comuna":"Ñuñoa","piscina":true} ###END### {"tipo_inmueble":"casa","precio_max":100000000,"moneda":"CLP"} ###END### {"comuna":"Santiago","precio_min":40000000,"precio_max":70000000,"moneda":"CLP"} ###END### {"tipo_inmueble":"departamento","precio_min":60000000,"precio_max":60000000,"moneda":"CLP","dormitorios":2} ###END### {"tipo_inmueble":"departamento","comuna":"Santiago","dormitorios":2,"banos":2,"estacionamientos":1} ###END### {"comuna":"Las Condes","piscina":true,"gimnasio":true} ###END### Ahora Normaliza el JSON según las reglas:
                  """}]


# Make the request with structured outputs
response = bedrock_runtime.converse(
    modelId=MODEL_ID,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "Mensaje del cliente: Casa en la florida con 2 baños"
                }
            ]
        },
    ],
)


# Parse the schema-compliant JSON response

# result = json.loads(response["output"]["message"]["content"][0]["text"])
# print(json.dumps(result, indent=2))




# result = response["output"]["message"]["content"][0]["text"]
print(response)