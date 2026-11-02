from samples.citation import (
    apa_author,
    bibtex_key,
    format_apa,
    format_bibtex,
    format_mla,
    initials,
    split_name,
)
from samples.models import PaperInfo

PAPER = PaperInfo(
    title="Attention Is All You Need",
    authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
    year=2017,
    venue="Neural Information Processing Systems",
    arxiv_id="1706.03762",
)


def test_split_name_handles_both_orders():
    assert split_name("Ashish Vaswani") == ("Ashish", "Vaswani")
    assert split_name("Vaswani, Ashish") == ("Ashish", "Vaswani")
    assert split_name("Plato") == ("", "Plato")


def test_initials():
    assert initials("Aidan N.") == "A. N."
    assert initials("Jean-Paul") == "J.-P."


def test_apa_author():
    assert apa_author("Ashish Vaswani") == "Vaswani, A."


def test_apa():
    assert format_apa(PAPER) == (
        "Vaswani, A., Shazeer, N., & Parmar, N. (2017). Attention Is All You Need. "
        "*Neural Information Processing Systems*. https://arxiv.org/abs/1706.03762"
    )


def test_apa_without_year_or_authors():
    assert format_apa(PaperInfo(title="Untitled draft")).startswith("(n.d.). Untitled draft.")


def test_mla_uses_et_al_for_three_or_more_authors():
    assert format_mla(PAPER) == (
        'Vaswani, Ashish, et al. "Attention Is All You Need." '
        "*Neural Information Processing Systems*, 2017. https://arxiv.org/abs/1706.03762."
    )


def test_mla_two_authors():
    two = PAPER.model_copy(update={"authors": ["Ashish Vaswani", "Noam Shazeer"]})
    assert format_mla(two).startswith("Vaswani, Ashish, and Noam Shazeer.")


def test_bibtex():
    bib = format_bibtex(PAPER)
    assert bib.startswith("@article{vaswani2017attention,")
    assert "author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki}" in bib
    assert "eprint = {1706.03762}" in bib


def test_bibtex_key_skips_stopwords():
    assert bibtex_key(PaperInfo(title="On the Origin of Species", year=1859)) == "unknown1859origin"
