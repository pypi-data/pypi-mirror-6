#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for Flask-Redis."""

import flask
from flask_pagination import paginate, url_for_other_page, Pagination
import unittest


class FlaskRedisTestCase(unittest.TestCase):

    def setUp(self):
        """ Create a sample Flask Application """
        self.app = flask.Flask(__name__)

        @self.app.route('/')
        @paginate
        def index(page, page_size):
            return "%s:%s" % (page, page_size)

        Pagination(self.app)

    def test_default_values(self):
        with self.app.test_client() as c:
            rv = c.get('/')
            assert rv.data == "1:20"

    def test_explicit_values(self):
        with self.app.test_client() as c:
            rv = c.get('/?page=2&page_size=40')
            assert rv.data == "2:40"

    def test_wrong_values(self):
        with self.app.test_client() as c:
            rv = c.get('/?page=-2&page_size=-40')
            assert rv.data == "1:20"

    def test_high_values(self):
        with self.app.test_client() as c:
            rv = c.get('/?page=6&page_size=-40')
            assert rv.data == "6:20"

    def test_url_for_other_page(self):
        with self.app.test_client() as c:
            rv = c.get('/')
            assert rv.data == "1:20"

            rv = c.get(url_for_other_page(2))
            assert rv.data == "2:20"
