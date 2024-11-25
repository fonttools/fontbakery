from fontbakery.prelude import PASS, FAIL


def check_repertoire(ttFont, character_repertoire, name, error_status=FAIL):
    charset = set(ttFont["cmap"].getBestCmap())
    missing = character_repertoire - charset
    if missing:
        missing_formatted = ", ".join(f"0x{v:04X}" for v in sorted(missing))
        yield error_status, (
            f"character repertoire not complete for {name}; missing: {missing_formatted}"
        )
    else:
        yield PASS, f"character repertoire complete for {name}"


def ensure_name_id_exists(ttFont, name_id, name_name, negative_status=FAIL):
    name_record = ttFont["name"].getName(name_id, 3, 1, 0x0409)
    if name_record is None:
        yield negative_status, f"Name ID {name_id} ({name_name}) does not exist."
    elif not name_record.toUnicode():
        yield negative_status, f"Name ID {name_id} ({name_name}) exists but is empty."
    else:
        yield PASS, f"Name ID {name_id} ({name_name}) exists and is not empty."
