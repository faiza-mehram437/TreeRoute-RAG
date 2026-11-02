import pytest

from samples.chunking import chunk_pages, chunk_text


def test_short_text_is_one_chunk():
    assert chunk_text("hello   world\n", size=100, overlap=10) == ["hello world"]


def test_empty_text_has_no_chunks():
    assert chunk_text("   \n ") == []


def test_chunks_respect_size_and_overlap():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = chunk_text(text, size=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
    # consecutive chunks share text
    assert chunks[0][-20:].split()[-1] in chunks[1]


def test_chunks_do_not_split_words():
    text = " ".join(f"token{i}" for i in range(300))
    for chunk in chunk_text(text, size=120, overlap=30):
        for word in chunk.split():
            assert word.startswith("token")


def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("abc", size=10, overlap=10)


def test_chunk_pages_keeps_page_numbers():
    chunks = chunk_pages([(1, "first page"), (3, "third page")], source="paper.pdf")
    assert [(c.page, c.text) for c in chunks] == [(1, "first page"), (3, "third page")]
    assert chunks[0].id == "paper.pdf:p1:c0"
