from app.domains.ingest.ingest_domain import (
    compute_url_hash,
    is_valid_candidate,
    map_category_slug,
    normalize_url,
    TitleDeduper,
)


def test_normalize_url_strips_utm():
    raw = "https://example.com/article?utm_source=twitter&id=1"
    assert normalize_url(raw) == "https://example.com/article?id=1"


def test_url_hash_stable():
    a = compute_url_hash("https://Example.com/path/")
    b = compute_url_hash("https://example.com/path")
    assert a == b


def test_title_min_length():
    assert not is_valid_candidate("short", "https://x.com")
    assert is_valid_candidate("long enough title", "https://x.com")


def test_map_category_slug():
    assert map_category_slug("technology", None) == "tech"
    assert map_category_slug(None, "it") == "it"


def test_title_deduper():
    deduper = TitleDeduper(titles=["OpenAI releases GPT model"])
    assert deduper.is_duplicate("OpenAI release GPT models")
    assert not deduper.is_duplicate("Completely different news headline today")
