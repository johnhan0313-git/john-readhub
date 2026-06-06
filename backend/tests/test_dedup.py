from app.services.dedup import normalize_url, url_hash


def test_normalize_url_strips_utm():
    raw = "https://example.com/article?utm_source=twitter&id=1"
    assert normalize_url(raw) == "https://example.com/article?id=1"


def test_url_hash_stable():
    a = url_hash("https://Example.com/path/")
    b = url_hash("https://example.com/path")
    assert a == b
