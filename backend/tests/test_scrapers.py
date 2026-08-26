from app.infrastructure.fetchers.scrapers.boss import BossZhipinFetcher
from app.infrastructure.fetchers.scrapers.liepin import LiepinFetcher


def test_boss_parse_joblist():
    data = {
        "code": 0,
        "zpData": {
            "jobList": [
                {
                    "jobName": "Python工程师",
                    "brandName": "示例科技",
                    "salaryDesc": "20-35K",
                    "cityName": "北京",
                    "encryptJobId": "abc123",
                }
            ]
        },
    }
    articles = BossZhipinFetcher()._parse_joblist(data, "Python")
    assert len(articles) == 1
    assert "Python工程师" in articles[0].title
    assert "示例科技" in articles[0].title
    assert articles[0].url.endswith("abc123.html")


def test_liepin_parse_payload():
    data = {
        "data": {
            "data": {
                "jobCardList": [
                    {
                        "job": {
                            "title": "Java开发",
                            "salary": "18-25k",
                            "dq": "北京",
                            "link": "https://www.liepin.com/job/1.shtml",
                        },
                        "comp": {"compName": "测试公司"},
                    }
                ]
            }
        }
    }
    articles = LiepinFetcher()._parse_payload(data, "Java")
    assert len(articles) == 1
    assert "Java开发" in articles[0].title
