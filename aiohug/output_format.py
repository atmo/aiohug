from functools import wraps
from typing import Optional, Callable


def content_type(content_type: str):
    """
    Decorator to create content type converters.
    :param content_type: HTTP header that corresponds to the media type that the decorator converter provides.
    :return: _ContentTypeConverter instance
    """

    def real_decorator(converter: Callable):
        wraps_decorator = wraps(converter)
        real_converter = wraps_decorator(_ContentTypeConverter(converter, content_type=content_type))
        return real_converter

    return real_decorator


class _ContentTypeConverter:
    def __init__(self, converter: Callable, content_type: str, charset: Optional[str] = None):
        self.converter = converter
        self.content_type = content_type
        self.charset = charset

    def __call__(self, content):
        return self.converter(content)

    def options(self, charset: str):
        return _ContentTypeConverter(self.converter, content_type=self.content_type, charset=charset)


@content_type("text/plain")
def text(content):
    """Free form UTF-8 text"""
    return str(content)


@content_type("text/html")
def html(content):
    """HTML (Hypertext Markup Language)"""
    return str(content)
