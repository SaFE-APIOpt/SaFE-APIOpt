import json
from openai import OpenAI
from pathlib import Path

# Initialize OpenAI client with your API key
client = OpenAI(
    api_key="YOUR_API_KEY_HERE"
)

# Path configuration
# train.json : The full FFmpeg API documentation (structured)
# safe_pairs.json : The generated SaFE API pairs
TRAIN_JSON_PATH = Path("train.json")
OUTPUT_JSON_PATH = Path("safe_pairs.json")

# Step 1 — Create a Vector Store
# A vector store is used for embedding-based retrieval over the FFmpeg API docs.
vector_store = client.vector_stores.create(
    name="ffmpeg_api_docs_store"
)
vector_store_id = vector_store.id
print("Vector store created:", vector_store_id)

# Step 2 — Upload the JSON documentation and index it into the vector store
# This enables the model to retrieve and reason over the FFmpeg API descriptions.

# Upload the document to OpenAI file storage
uploaded_file = client.files.create(
    file=open(TRAIN_JSON_PATH, "rb"),
    purpose="assistants"
)
print("Uploaded file:", uploaded_file.id)

file_batch = client.vector_stores.files.create_and_poll(
    vector_store_id=vector_store_id,
    file_id=uploaded_file.id,
)
print("File indexing finished:", file_batch.status)

# Step 3 — Prompt describing the SaFE API extraction task
# This prompt defines the concept of Scenario-aware Functional Equivalent APIs
# and instructs the model to output only a JSON array.
BASE_PROMPT = """
You are an expert in the internals of the FFmpeg multimedia framework, including libavutil, libavcodec, libavformat, libswscale, and libswresample. I will provide you with a JSON file that contains structured documentation of a large collection of FFmpeg APIs. Your goal is to analyze these APIs, understand their functionality, their parameters, data dependencies, constraints, and typical usage contexts, and then infer which combinations of APIs can be considered Scenario-aware Functional Equivalent (SaFE) API pairs.

A Scenario-aware Functional Equivalent (SaFE) API pair refers to two APIs that, regardless of whether they were originally designed for exactly the same function, can be used interchangeably under certain constrained and well-defined application scenarios to achieve equivalent functionality. This means that although the APIs may differ in general design goals or behavior, they can still produce the same observable effect, the same output, or an equivalently acceptable result, provided that specific contextual conditions—such as matching pixel formats, channel layouts, memory layouts, buffer alignments, parameter ranges, resource state, or other scenario constraints—are satisfied. Under such scenarios, the caller can replace one API with the other without breaking the correctness or functionality of the target task.

Your task is to examine all APIs in the provided JSON documentation, identify all potential SaFE API pairs, and explain for each pair the scenario in which the two APIs become effectively equivalent. You must rely strictly on FFmpeg’s API semantics, typical use cases, and logically valid reasoning grounded in the documentation. Your output must only contain a JSON array, where each element includes: a unique pair_id, an api_1 object containing name and description, an api_2 object containing name and description, and a scenario_equivalence_reason describing why these APIs are functionally interchangeable under the scenario you identify.

Return only a JSON array.
""".strip()

# Step 4 — Query GPT-4.1 with Retrieval (file_search tool)
# The model uses the vector store to retrieve relevant API descriptions before
# generating SaFE API pairs.
response = client.responses.create(
    model="gpt-4.1",
    input=BASE_PROMPT,
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [vector_store_id],
            "max_num_results": 50,
        }
    ],
    include=["file_search_call.results"],
)

print("\nModel response received.\n")

# Step 5 — Extract the model-generated JSON output
# The new API returns output blocks; we search for the one containing text.
result_text = None

for item in response.output:
    if hasattr(item, "content") and item.content:
        for block in item.content:
            if block.type == "output_text":
                result_text = block.text
                break
    if result_text:
        break

if result_text is None:
    raise RuntimeError("No output_text found — The model did not return a textual response.")

safe_pairs = json.loads(result_text)

# Step 6 — Save extracted SaFE API pairs to disk
OUTPUT_JSON_PATH.write_text(
    json.dumps(safe_pairs, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print("SaFE API pairs saved to:", OUTPUT_JSON_PATH)
