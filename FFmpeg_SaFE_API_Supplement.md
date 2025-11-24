### Automatic Extraction of SaFE API Pairs from FFmpeg

This repository contains the implementation of an auxiliary experiment from our research, designed to validate that our method for discovering *Scenario-aware Functional Equivalent (SaFE) APIs* does not rely on StackOverflow .

Instead, this experiment demonstrates that SaFE API pairs can be inferred directly from structured FFmpeg API documentation, using retrieval-augmented generation (RAG) and an LLM.

The script in this repository loads FFmpeg API documentation (in JSON format), stores it into a vector database, performs semantic retrieval, and uses LLM to automatically generate SaFE API pairs together with the scenario constraints under which equivalence holds.



#### Input Data (train.json)

Extracted manually from FFmpeg headers and documentation, and converted into machine-readable JSON format.

Example entry:

```json
{
  "function_name": "av_image_get_buffer_size",
  "declaration": "int av_image_get_buffer_size(enum AVPixelFormat pix_fmt, int width, int height, int align)",
  "description": "Return required buffer size for storing an image of given format and dimensions.",
  "parameters": {
    "pix_fmt": "pixel format",
    "width": "width in pixels",
    "height": "height in pixels",
    "align": "linesize alignment"
  },
  "returns": "Required size in bytes or negative error."
}

```

#### Run the Script

```
python generate_safe_pairs_from_ffmpeg_docs.py
```

The generated SaFE API pairs will be saved as: **safe_pairs.json**

Example output:

```json
{
    "pair_id": "1",
    "api_1": {
      "name": "av_buffer_pool_init",
      "description": "Allocate and initialize a buffer pool. Parameters: size of each buffer; alloc (allocator function, may be NULL for default allocator). Returns a newly created buffer pool, or NULL on error."
    },
    "api_2": {
      "name": "av_buffer_pool_init2",
      "description": "Allocate and initialize a buffer pool with a more complex allocator. Parameters: size of each buffer, arbitrary user data, allocator function for new buffers, and pool_free (cleanup for user data). Returns newly created pool or NULL on error."
    },
    "scenario_equivalence_reason": "Both functions create buffer pools for memory management and are functionally interchangeable when the buffer allocator does not require arbitrary user data or a custom cleanup function. If alloc is NULL, both will use av_buffer_alloc(); if alloc is non-NULL and does not require 'opaque', av_buffer_pool_init2 behaves identically to av_buffer_pool_init. In scenarios where no custom state or cleanup is needed, either API may be used to initialize a buffer pool."
}
```

