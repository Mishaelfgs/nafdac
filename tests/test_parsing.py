from datetime import date

from app.core.parsing import format_nafdac, normalise_nafdac, parse_message


def test_normalise_formats():
    assert normalise_nafdac("A4-1001") == "A41001"
    assert normalise_nafdac("a4 1001") == "A41001"
    assert normalise_nafdac("01-2001") == "012001"
    assert normalise_nafdac("B1-0123") == "B10123"
    assert format_nafdac("A41001") == "A4-1001"


def test_normalise_fixes_typos():
    assert normalise_nafdac("A4-1OO1") == "A41001"     # letter O for zero
    assert normalise_nafdac("O1-2001") == "012001"
    assert normalise_nafdac("hello") is None


def test_parse_full_message():
    p = parse_message("Please check NAFDAC No: A4-1001 batch ab12 exp 12/2026")
    assert p.nafdac_key == "A41001" and p.batch == "AB12" and p.expiry == date(2026, 12, 31)


def test_number_not_confused_with_expiry():
    p = parse_message("01-2001")            # valid NAFDAC format that also looks like MM-YYYY
    assert p.nafdac_key == "012001" and p.expiry is None


def test_name_and_maker():
    p = parse_message("Sample Paracetamol | Sample Pharma Ltd")
    assert p.name == "Sample Paracetamol" and p.manufacturer == "Sample Pharma Ltd" and p.nafdac_key is None


def test_phone_number_not_read_as_nafdac():
    assert parse_message("08012345678").nafdac_key is None
