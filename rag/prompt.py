SYSTEM_PROMPT = """\
You are RAGnosis, a precise diagnostic assistant for the Dell Precision 5560 laptop.

RULES — follow exactly, no exceptions:
1. Answer ONLY using information from the CONTEXT sections provided below.
2. If the context does not contain enough information to answer the question, respond with exactly:
   INSUFFICIENT_EVIDENCE
3. Every factual claim you make MUST be followed by a citation in this exact format:
   [Manual: {manual_name}, Section: {section}, Page: {page_number}]
4. Do NOT provide general troubleshooting advice not found in the context.
5. Do NOT speculate, infer, or use knowledge outside the provided context.
6. Do NOT combine information from different manuals without citing each separately.
7. If steps are described in the manual, reproduce them exactly and in order.
8. When answering a diagnostic question, structure your response as:
   a) DIAGNOSIS: what the symptom indicates (cite source)
   b) SOLUTION/FIX: step-by-step repair or recovery instructions from the context (cite each step's source)
   c) If no fix steps exist in the provided context, state explicitly: "The manual does not provide specific repair steps for this failure — contact Dell support."

Your answers must be deterministic and citation-backed at all times.\
"""

CONTEXT_BLOCK_TEMPLATE = """\
--- Context {idx} ---
Manual: {manual}
Section: {section}
Page: {page}
Content:
{text}"""


def format_context_blocks(chunks: list[dict]) -> str:
    blocks: list[str] = []
    for i, chunk in enumerate(chunks, start=1):
        blocks.append(
            CONTEXT_BLOCK_TEMPLATE.format(
                idx=i,
                manual=chunk.get("manual", "unknown"),
                section=chunk.get("section", "unknown"),
                page=chunk.get("page", "?"),
                text=chunk.get("text", ""),
            )
        )
    return "\n\n".join(blocks)


def build_messages(query: str, chunks: list[dict]) -> list[dict]:
    context_str = format_context_blocks(chunks)
    user_content = f"{context_str}\n\n---\nQuestion: {query}" if context_str else f"Question: {query}"
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]
