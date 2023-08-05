# -*- coding: utf-8 -*-
"""
"""
from nozama.cloudsearch.data import document
#from nozama.cloudsearch.data.db import get_es


def test_search_with_no_content(logger, mongodb, elastic):
    """Test search an empty system doesn't raise exceptions.
    """
    assert document.all() == []

    results = document.search()
    assert results['hits']['found'] == 0


def test_basic_search(logger, mongodb, elastic):
    """Test searching the documents stored in mongodb.
    """
    assert document.all() == []

    doc = {
        "designer": "GearPro",
        "price": 12.60,
        "retailer": "MyShoppe",
        "brand_id": [
            7017
        ],
        "size": [],
        "category": "",
        "name": "Pro Quad Clamp Purple",
        "colour": [],
        "brand": "98",
        "created_at": 1376391294
    }

    doc2 = {
        "designer": "GearPro",
        "price": 12.60,
        "retailer": "MyShoppe",
        "brand_id": [
            7016
        ],
        "size": [],
        "category": "",
        "name": "Bike Pump Purple",
        "colour": [],
        "brand": "98",
        "created_at": 1376391294
    }

    example_sdf = [
        {
            "lang": "en",
            "fields": doc,
            "version": 1376497963,
            "type": "add",
            "id": 1246
        },
        {
            "lang": "en",
            "fields": doc2,
            "version": 1376497963,
            "type": "add",
            "id": 1247
        }
    ]

    rc = document.load(example_sdf)
    assert rc['status'] == 'ok'
    assert rc['adds'] == 2

    # return all:
    results = document.search()
    assert results['hits']['found'] == 2
    c = [{'id': '1247'}, {'id': '1246'}]
    c.sort()
    results['hits']['hit'].sort()
    assert results['hits']['hit'] == c

    # return a specific one:
    query = dict(q="pro")
    results = document.search(query)
    assert results['hits']['found'] == 1
    assert results['hits']['hit'] == [{'id': '1246'}]

    query = dict(q="myshop")
    results = document.search(query)
    assert results['hits']['found'] == 2
    c.sort()
    results['hits']['hit'].sort()
    assert results['hits']['hit'] == c

    query = dict(q="not in any string")
    results = document.search(query)
    assert results['hits']['found'] == 0
