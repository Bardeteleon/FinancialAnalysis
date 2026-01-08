from datetime import date
from statement.EntryMapping import EntryMapping
from data_types.InterpretedEntry import InterpretedEntry


def test_entries_per_year_and_week():
    entry1 = InterpretedEntry(date=date(2024, 12, 28))
    entry2 = InterpretedEntry(date=date(2025, 1, 6))
    entry3 = InterpretedEntry(date=date(2025, 1, 7))
    entry4 = InterpretedEntry(date=date(2025, 1, 13))
    entry5 = InterpretedEntry(date=date(2026, 1, 5))
    entry6 = InterpretedEntry(date=date(2026, 1, 12))

    entries = [entry1, entry2, entry3, entry4, entry5, entry6]

    result = EntryMapping.entries_per_year_and_week(entries)

    assert result[2024][52] == [entry1]
    assert result[2025][2] == [entry2, entry3]
    assert result[2025][3] == [entry4]
    assert result[2026][2] == [entry5]
    assert result[2026][3] == [entry6]
