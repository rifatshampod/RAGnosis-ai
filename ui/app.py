from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="RAGnosis AI",
    page_icon="🔧",
    layout="wide",
)


def get_health() -> dict:
    try:
        r = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return r.json()
    except Exception:
        return {"status": "unreachable", "chunks_indexed": 0, "embed_model": "unknown"}


def ask(query: str, top_k: int = 5) -> dict:
    r = requests.post(
        f"{API_BASE_URL}/chat",
        json={"query": query, "top_k": top_k},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("RAGnosis AI")
    st.caption("Dell Precision 5560 Diagnostic Assistant")
    st.divider()

    health = get_health()
    status_color = "🟢" if health["status"] == "ok" else "🔴"
    st.markdown(f"{status_color} **API status:** {health['status']}")
    st.markdown(f"📚 **Chunks indexed:** {health['chunks_indexed']:,}")
    st.markdown(f"🧠 **Embed model:** {health['embed_model']}")

    st.divider()
    st.warning(
        "Answers are sourced **exclusively** from official Dell Precision 5560 "
        "service manuals. No general advice or internet data is used."
    )

    top_k = st.slider("Results to retrieve (top-k)", min_value=1, max_value=10, value=5)

    if st.button("Clear chat"):
        st.session_state["messages"] = []
        st.rerun()


# ── Main ─────────────────────────────────────────────────────────────────────
st.title("🔧 RAGnosis AI")
st.caption("Ask any hardware question about the Dell Precision 5560. Answers cite official manuals.")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for query, response in st.session_state["messages"]:
    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        if response.get("insufficient_evidence"):
            st.error(response["answer"])
        else:
            st.markdown(response["answer"])
            if response.get("citations"):
                with st.expander("📎 Sources", expanded=False):
                    for c in response["citations"]:
                        st.markdown(
                            f"- **{c['manual']}** — {c['section']} — Page {c['page']}"
                        )

query_input = st.chat_input("Describe your issue or ask a question about the Dell Precision 5560...")

if query_input:
    with st.chat_message("user"):
        st.write(query_input)

    with st.chat_message("assistant"):
        with st.spinner("Searching manuals..."):
            try:
                response = ask(query_input, top_k=top_k)
            except Exception as e:
                st.error(f"API error: {e}")
                response = {
                    "answer": str(e),
                    "citations": [],
                    "insufficient_evidence": True,
                    "model": "error",
                }

        if response.get("insufficient_evidence"):
            st.error(response["answer"])
        else:
            st.markdown(response["answer"])
            if response.get("citations"):
                with st.expander("📎 Sources", expanded=True):
                    for c in response["citations"]:
                        st.markdown(
                            f"- **{c['manual']}** — {c['section']} — Page {c['page']}"
                        )

    st.session_state["messages"].append((query_input, response))
