extraction_schema = {
    "type": "object",
    "properties": {
        "tipo_inmueble": {
            "type": "string",
            "enum": ["casa", "departamento"],
            "description": "Tipo de inmueble: casa o departamento. Puede estar mal escrito o usar modismos locales, debes intentar definir si se refiere a casa o departamento."
        },
        "comuna": {
            "type": "string",
            "enum": ["la florida", "las condes", "providencia", "santiago", "ñuñoa"],
            "description": "Nombre de la comuna en Chile"
        },
        "dormitorios": {
            "type": "integer",
            "description": "Cantidad de dormitorios."
        },
        "banos": {
            "type": "integer",
            "description": "Cantidad de baños."
        },
        "precio": {
            "type": "number",
            "description": "Valor mínimo o exacto del precio"
        },
    },
    "required": ["tipo_inmueble"],
    "additionalProperties": False
}
