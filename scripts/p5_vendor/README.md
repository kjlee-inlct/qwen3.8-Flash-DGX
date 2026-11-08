# P5 source auditor provenance

This directory contains the unmodified YSLAB-ai reference `src/recipe/{manifest,audit,mtp,safetensors}.py` and pinned `compatibility.json`, copied from commit `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` under Apache-2.0, with upstream LICENSE and NOTICE. The enclosing package `__init__.py` was added for Blazux.

The reference metadata/safetensors audit and MTP overlay construction are source utilities only. They do **not** install YSLAB's vLLM development image, validate vLLM 0.32 CUDA ABI, or confer permission to create multi-GiB derived views. The imported overlay builder is intentionally not callable through the P5 CLI until separate asset-write approval and runtime validation. The YSLAB Dockerfile, model class patches, and vLLM PLE module are deliberately **not** vendored.

P5 uses the existing Blazux `src/vllm_ple_mmap.py` BF16-capable source as a candidate, not as DGX GPU proof. Source pin/hash/shape auditing may pass while GPU/API/MTP2 remain NOT_RUN.
