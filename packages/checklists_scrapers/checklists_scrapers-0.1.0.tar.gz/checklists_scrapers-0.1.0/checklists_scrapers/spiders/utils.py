"""Utility functions used by the scrapers to parse content."""

import json
import re


def remove_whitespace(strings):
    """Remove whitespace and empty strings.

    Args:
        strings (list): an list of strings containing whitespace.

    Returns:
       list: the strings with extra whitespace and blank strings removed,

    Use this to cleanup strings extracted from HTML using XPath
    expressions where extra whitespace is included, typically by
    template engines, but not displayed by browsers.
    """
    cleaned = [re.sub(r'(\s+)', ' ', string, flags=re.UNICODE).strip()
               for string in strings]
    return filter(None, cleaned)


def select_keys(records, keys):
    """Filter the records extracting only the selected fields.

    Args:
        records (list(dict)): the list of dicts to be filtered.
        keys (list(str)): the keys to select from the records.

    Returns:
        list(dict): the list of records containing only the specified keys.

    The returned list is in the same order as the original records.
    """
    filtered = []
    for record in records:
        filtered.append({key: record[key] for key in keys if key in record})
    return filtered


def dedup(records):
    """Remove any identical records from the list.

    Args:
        records (list(dict)): the list of dicts to be filtered.

    Returns:
        list(dict): the list of records with any duplicates removed.

    The list returned contains records in the same order as the original list.
    """
    seen = set()
    filtered = []
    for record in records:
        key = tuple(sorted(record.items()))
        if key not in seen:
            seen.add(key)
            filtered.append(record)
    return filtered


def save_json_data(path, data):
    """Write the data in JSON format to a file.

    Args:
        path (str): the path where the checklists will be saved.
        checklist (dict): a dict that will be encoded in JSON format and
            written to a file.
    """
    with open(path, 'wb') as fp:
        json.dump(data, fp)
