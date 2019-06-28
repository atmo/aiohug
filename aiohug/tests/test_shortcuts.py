import json

import pytest
from aiohttp import web

from aiohug.output_format import text
from aiohug.shortcuts import process_response, json_response


def test_plaintext():
    text = "pong"
    resp = process_response(text)
    expected = web.Response(text=text)
    assert resp.text == expected.text
    assert resp.content_type == expected.content_type


@pytest.mark.parametrize("body", ({"message": "hello"}, [{"message": "hello"}]))
def test_json(body):
    response = process_response(body)
    expected_response = web.Response(text=json.dumps(body), content_type="application/json")
    assert response.body == expected_response.body
    assert response.content_type == expected_response.content_type


@pytest.mark.parametrize("body", ({"message": "hello"}, [{"message": "hello"}]))
def test_status_and_body(body):
    status = 201
    response = process_response((status, body))
    expected_response = web.Response(text=json.dumps(body), content_type="application/json", status=status)
    assert response.status == expected_response.status
    assert response.body == expected_response.body


def test_no_shortcut():
    response = web.Response(text="foo")
    assert process_response(response) == response


@pytest.mark.parametrize("body, processed_body", ((5, "5"), (5.0, "5.0")))
def test_default_shortcut(body, processed_body):
    response = process_response(body)
    assert response.text == processed_body


@pytest.mark.parametrize(
    "body, output, response_text, response_charset",
    (
        ({"foo": "bar"}, text, '{"foo": "bar"}', "utf-8"),
        ("foo", text, 'foo', "utf-8"),
        ("foo", text.options(charset="cp1251"), 'foo', "cp1251"),
    ),
)
def test_shortcut_with_output(body, output, response_text, response_charset):
    response = process_response(body, output)
    assert response.text == response_text
    assert response.charset == response_charset


@pytest.mark.parametrize("data, text, body", (({}, "foo", "bar"), ({}, "foo", None), ({}, None, "bar")))
def test_json_response_raises(data, text, body):
    with pytest.raises(ValueError):
        json_response(data=data, text=text, body=body)


def test_json_response_no_data():
    assert json_response(text="[]").text == "[]"


def test_json_response_defaults():
    response = json_response(text="[]")
    assert response.content_type == "application/json"
    assert response.charset == "utf-8"
