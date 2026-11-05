from app.core.engine import Verdict, check_input

V = Verdict


def test_verified_no_barcode_needed(db):            # product has NO barcode and is still verified
    r = check_input(db, "SMPL-0001")
    assert r.verdict == V.VERIFIED and r.product.barcode is None


def test_verified_lowercase_and_spaces(db):
    assert check_input(db, "smpl 0002").verdict == V.VERIFIED


def test_not_found(db):
    assert check_input(db, "SMPL-9999").verdict == V.NOT_FOUND


def test_mistyped_number_letter_o(db):
    assert check_input(db, "SMPL-0O01").verdict == V.VERIFIED       # O->0 typo auto-fixed


def test_mistyped_number_suggests_close_match(db):
    r = check_input(db, "SMPL-0004")                                 # one digit away from real records
    assert r.verdict == V.NOT_FOUND and r.suggestions               # "did you mean ...?"


def test_expired_batch(db):
    assert check_input(db, "SMPL-0001 EXP 01/2020").verdict == V.EXPIRED


def test_future_expiry_ok(db):
    assert check_input(db, "SMPL-0001 EXP 12/2099").verdict == V.VERIFIED


def test_recalled_product(db):
    assert check_input(db, "SMPL-0003").verdict == V.RECALLED


def test_recalled_batch_only(db):
    assert check_input(db, "A4-1001 batch BAD99").verdict == V.RECALLED
    assert check_input(db, "A4-1001 batch GOOD1").verdict == V.VERIFIED


def test_suspicious_maker_mismatch_with_number(db):
    r = check_input(db, "SMPL-0001 | Sample Paracetamol 500mg Tablets | Totally Different Pharma")
    assert r.verdict == V.SUSPICIOUS and "maker_mismatch" in r.reasons


def test_chatter_does_not_cause_suspicious(db):
    assert check_input(db, "pls check this one SMPL-0001").verdict == V.VERIFIED


def test_no_nafdac_on_pack_is_suspicious(db):
    assert check_input(db, "NONE").verdict == V.SUSPICIOUS


def test_name_and_maker_verified(db):
    assert check_input(db, "Sample Paracetamol 500mg | Sample Pharma").verdict == V.VERIFIED


def test_name_with_wrong_maker_suspicious(db):
    assert check_input(db, "Sample Paracetamol 500mg | Wrong Company").verdict == V.SUSPICIOUS


def test_name_only_needs_more_info(db):
    r = check_input(db, "Sample Paracetamol 500mg")
    assert r.verdict == V.NEED_MORE_INFO and r.suggestions


def test_unknown_name_not_found(db):
    assert check_input(db, "Zzzqx Wonder Elixir | Nobody Ltd").verdict == V.NOT_FOUND


def test_gibberish_or_incomplete(db):
    assert check_input(db, "??").verdict == V.NEED_MORE_INFO
    assert check_input(db, "BATCH 123 EXP 12/2026").verdict == V.NEED_MORE_INFO
