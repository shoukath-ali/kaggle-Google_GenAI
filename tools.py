## adding tool -
from langchain_core.tools import tool
from dataprep import chunks


@tool
def get_data() -> str:
    """Provide the latest up-to-date analysis"""
    # Note that this is just hard-coded text, but you could connect this to a live stock
    # database, or you could use Gemini's multi-modal capabilities and take live photos of
    # your cafe's chalk menu or the products on the counter and assmble them into an input.
    

    return str(chunks)