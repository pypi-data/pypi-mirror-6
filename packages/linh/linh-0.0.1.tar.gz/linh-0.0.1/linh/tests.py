from django.test import TestCase


class LinhTestCase(TestCase):

    def assertTokenListEqual(self, list1, list2, msg=None):
        for token1, token2 in zip(list1, list2):
            return self.assertTokenEqual(token1, token2, msg)

    def assertTokenEqual(self, token1, token2, msg=None):
        return self.assertEqual(token1.contents, token2.contents, msg)


class Test(LinhTestCase):

    def test_vai(self):
        pass

        # from django.template import Template
        # from django.template.base import Lexer, Parser, Token
        # from django.template.base import (TOKEN_TEXT, TOKEN_VAR, TOKEN_BLOCK, TOKEN_COMMENT)
        # from django.template.context import Context

        # from pprint import pprint as pp
        # import cPickle as pickle

        # tokens = [
        #     Token(TOKEN_TEXT, "<h1>"),
        #     Token(TOKEN_VAR, "oi|default:'sim'"),
        #     Token(TOKEN_TEXT, "</h1>"),
        # ]

        # s = pickle.dumps(tokens)
        # data = pickle.loads(s)

        # self.assertTokenListEqual(tokens, data)

        # parser = Parser(data)
        # nodes = parser.parse()
        # context = Context({})
        #pp( nodes.render(context) )