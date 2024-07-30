from langsmith import Client
import requests
import os
import pprint
import json
import orjson

if __name__ == "__main__":
    client = Client()

    run_id = "bee844d5-dd70-4666-a08b-cead656f1cda"
    # run = client.read_run(run_id=run_id)

    # inputs = run.inputs
    # outputs = run.outputs

    # pp = pprint.PrettyPrinter(indent=4)
    # print("\nInput:")
    # pp.pprint(inputs)
    # print("\nOutput:")
    # pp.pprint(outputs)

    LANGSMITH_API_URL = "https://api.smith.langchain.com"
    request_url = f"{LANGSMITH_API_URL}/runs/{run_id}"
    data = {"extra": {"metadata": {"new-key": "new-value"}}}
    data = orjson.dumps(
            data,
            default=None,
            option=orjson.OPT_SERIALIZE_NUMPY
            | orjson.OPT_SERIALIZE_DATACLASS
            | orjson.OPT_SERIALIZE_UUID
            | orjson.OPT_NON_STR_KEYS,
        )
    
    request_kwargs = {
    "data": data,  # Change 'data' to 'json'
    "headers": {
        "Content-Type": "application/json",  # This can actually be omitted when using 'json'
        "x-api-key": os.getenv("LANGCHAIN_API_KEY")
    },
}

    session = requests.Session()
    response = session.request(
        "PATCH",
        request_url,
        stream=False,
        **request_kwargs,
    )
    
    # print(response.json())

    print(client.read_run(run_id=run_id))
