import unittest
import datetime as dt
from parameterized import parameterized
import time

from . import read_fixture
from .. import dates
from .. import webpages

import pytest
import re
from surt import surt

@pytest.fixture
def use_cache(request):
    return request.config.getoption('--use-cache')

def filesafe_url(url):
    url = re.sub('"', "", url)
    s = surt(url) 
    filesafe_surt = "cached-"+re.sub("\W+", "", url)
    return filesafe_surt


class TestDates(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def get_use_cache(self, use_cache):
        self.use_cache = use_cache

    def tearDown(self):
        time.sleep(1)  # sleep time in seconds

    @parameterized.expand([
        # subhead
        ("https://web.archive.org/web/https://www.sun-sentinel.com/community/fl-cn-calendar-events-20211201-20211129-sv3syeeuwzeallnr4vcanvaeti-story.html", dt.date(2021, 11, 29)),
        # in url
        ("https://web.archive.org/web/https://www.cnn.com/2021/04/30/politics/mcconnell-1619-project-education-secretary/index.html", dt.date(2021, 4, 30)),
        # in meta tag
        ("https://web.archive.org/web/https://www.foxnews.com/politics/biden-cancel-school-loans-corinthian-college-students", dt.date(2022, 6, 1)),
        # ignore footer copyright
        ("https://web.archive.org/web/https://www.alliedmarketresearch.com/cytogenetics-market", None),
        ("https://web.archive.org/web/https://www.bakerbotts.com/footer/subscribe", None),
        ("https://web.archive.org/web/https://www.kingjamesbibleonline.org/1-Chronicles-Chapter-1/", None),
        ("https://web.archive.org/web/https://www.womblebonddickinson.com/us/people-search", None),
        # ordered day month year
        ("https://web.archive.org/web/https://www.eeas.europa.eu/eeas/eu-world-0_en", dt.date(2022, 3, 30)),
        # undateable
        ("http://archive.org", None),
        # real site
        ("https://web.archive.org/web/https://www.atv.hu/belfold/20190730/gyarfas-ugyvedje-aki-a-vadiratot-alkotta-nem-biztos-hogy-az-ugy-minden-reszletet-megismerte", dt.date(2019, 7, 30)),
        # slow site
        ("http://www.diariobahiadecadiz.com/noticias/san-fernando/cavada-y-romero-mantienen-otro-encuentro-con-defensa-para-negociar-la-desafectacion-de-suelo-en-camposoto-requerira-un-tiempo-indeterminado/", dt.date(2016, 10, 13))
    ])
    def test_pub_date(self, url, expected_date):
        
        if(self.use_cache):
            try:
                raw_html = read_fixture(filesafe_url(url))
            except:
                raw_html, _ = webpages.fetch(url, timeout=120)
        else:
            raw_html, _ = webpages.fetch(url, timeout=120)

        
        pub_date = dates.guess_publication_date(raw_html, url)
        if expected_date is None:
            assert pub_date is None
        else:
            assert pub_date.date() == expected_date

    def test_max_date(self):
        u = "https://web.archive.org/web/https://www.canarias7.es/cultura/cimientos-artes-escenicas-20220718203045-nt.html"
        raw_html, response = webpages.fetch(u)
        date = dates.guess_publication_date(raw_html, u)
        assert date.date() == dt.date(2022, 7, 17)
        date = dates.guess_publication_date(raw_html, u, max_date=dt.datetime(2020, 1, 1))
        assert date is None
