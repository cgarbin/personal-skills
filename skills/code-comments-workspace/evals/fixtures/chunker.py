"""Markdown chunking utilities for the retrieval corpus."""

# Cluster A1: chunking. Step 3 of the ingestion plan.

MAX_CHARS = 8192
OVERLAP = 200


def is_table_start(line: str, next_line: str) -> bool:
    """Table start boolean predicate determination for markdown line pairs.

    Returns True if the line starts a table. The indexer calls this to decide
    whether to keep rows together, and split_markdown() uses the result in its
    inner loop where it walks the line list and accumulates a buffer until the
    buffer exceeds MAX_CHARS.

    We considered a regex-based detector that matched the delimiter row alone,
    but it produced false positives on horizontal rules, so we went with the
    two-line lookahead instead.
    """
    if not line.strip().startswith("|"):
        return False
    # Guard against the canonical delimiter form.
    return set(next_line.strip()) <= set("|-: ")


def split_markdown(text: str) -> list[str]:
    """Split markdown text into chunks.

    Takes a string and returns a list of strings.
    """
    # This used to call normalize_headings() before splitting, but that no
    # longer runs after we decoupled the normalizer.
    chunks: list[str] = []
    buf: list[str] = []
    size = 0

    lines = text.splitlines()
    # Callers always pass a non-empty string, so lines is never empty.
    i = 0
    while i < len(lines):
        next_line = lines[i + 1] if i + 1 < len(lines) else ""
        block = [lines[i]]
        if is_table_start(lines[i], next_line):
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j])
                j += 1
            i = j
        else:
            i += 1

        # Set the running size.
        block_size = sum(len(x) + 1 for x in block)

        # 8192 is the largest input the tokenizer accepts in one call.
        if buf and size + block_size > MAX_CHARS:
            chunks.append("\n".join(buf))
            while buf and sum(len(x) + 1 for x in buf) > OVERLAP:
                buf.pop(0)
            size = sum(len(x) + 1 for x in buf)

        buf.extend(block)
        size += block_size

    if buf:
        chunks.append("\n".join(buf))

    # The caller uses this list to build the embedding batch, and the empty
    # case means the batch builder skips the document entirely.
    return chunks


def chunk_document(path: str) -> list[str]:
    """Chunk a document at a path.

    The operation is idempotent. Rows that drift apart from their header row
    lose the column names.
    """
    # This function is load-bearing for the downstream index build.
    #
    # We benchmarked reading the whole file against streaming it line by line
    # and the whole-file read won for documents under 50 MB, so it stayed.
    with open(path) as f:
        return split_markdown(f.read())
