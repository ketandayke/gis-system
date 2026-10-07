import pytest
from app.services.parser_service import parse_file, GISParserError

def test_parse_invalid_file():
    with pytest.raises(GISParserError):
        parse_file("nonexistent.kml", "kml")
