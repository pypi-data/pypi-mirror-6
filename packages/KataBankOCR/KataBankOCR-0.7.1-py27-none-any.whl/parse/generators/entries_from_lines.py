"generator that yields Entries"

from parse import settings

def entries_from_lines(lines):
    "generator that reads Lines and yields Entries"
    entry = []
    for line in lines:
        entry.append(line)
        if len(entry) == settings.lines_per_entry:
            yield entry
            entry = []
    if entry:
        raise(ValueError('File ended mid-entry'))
