# elastic_schema.py

elastic_schema_mapping = {
    "mappings": {
        "properties": {
            "content": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
                    }
                }
            },
            "embedding": {
                "type": "dense_vector",
                "dims": 1536  # Adjust based on your embedding size
            }
        }
    }
}