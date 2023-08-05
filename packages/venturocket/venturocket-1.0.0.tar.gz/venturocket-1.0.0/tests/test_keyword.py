from venturocket.keyword import KeywordClient

__author__ = 'Joe Linn'

import unittest
from tests.basetest import BaseTest


class KeywordClientTest(BaseTest):

    def setUp(self):
        super(KeywordClientTest, self).setUp()
        self._client = KeywordClient(self._key, self._secret)

    def test_get_keyword(self):
        word = "php"
        keyword = self._client.get_keyword(word)
        self.assertEqual(word, keyword['word'])

    def test_get_suggestions(self):
        suggestions = self._client.get_suggestions("php", "python", "java")
        self.assertGreater(len(suggestions), 0)

    def test_parse_keywords(self):
        text = """
            We are looking for rock star Web Developer with expertise in Javascript and PHP. This is a great opportunity to define and implement interactive technologies that will have a positive social impact on millions of users. You will be part of a passionate and high energy team that is creating compelling, new and innovative online technologies. The ideal candidate will have experience building and working with ecommerce and dynamic image generation. This position requires someone who thrives on finding innovative solutions to real problems.
            Job Responsibilities:
            Work with 3rd party shopping cart solutions by enabling users around the globe to make payments
            Work on innovative email security platform to enable users communicate privately
            Design, develop and test new software products while also supporting existing commercial products
            Develop related applications/utilities, widgets, and help build out our platform
            Work with web proxies, enhancing content delivery performance
            Provide creativity and new, fresh ideas
            Job Qualifications:
            Proven experience in developing frameworks and UI for web-based payments: authentication, account management, integration with payment gateways, transaction history, credits and refunds.
            Recent hands-on with LAMP (Linux, Apache, MySql, PHP) and open source development
            Expertise in HTML, CSS, DOM, AJAX; deep understanding of cookies, client-side storage.
            Experience with cross-platform, cross-browser development
            A track record of delivering quality bug-free code on schedule
            Preferable Job Qualifications:
            Experience with web proxies
            JavaScript experience
            Web Design Skills (Photoshop, Illustrator)
            Open Source contribution is a plus
            BS in Computer Science or equivalent job experience
        """
        keywords = self._client.parse_keywords(text)
        self.assertTrue("php" in keywords)


if __name__ == '__main__':
    unittest.main()
