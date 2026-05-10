"""
Remove duplicate token row 60 (second 'did') from sent_246 in filled-10.conllu.
Then renumber tokens 61-110 down by 1 (to 60-109) and update HEAD references accordingly.
"""

filepath = r"c:/Users/bibleman/repos/readers-bofm/data/parses/llm-direct/3nephi-batches/filled-10.conllu"

with open(filepath, encoding="utf-8") as f:
    lines = f.readlines()

# Find sent_246 boundaries
start_246 = None
end_246 = None
for i, line in enumerate(lines):
    if "# sent_id = 246" in line:
        start_246 = i
    if start_246 is not None and i > start_246 and line.strip() == "":
        end_246 = i
        break

print(f"sent_246 spans lines {start_246}-{end_246}")

# Identify the duplicate token 60 line within sent_246
dup_line_idx = None
for i in range(start_246, end_246):
    line = lines[i].rstrip()
    parts = line.split("\t")
    if len(parts) >= 2 and parts[0] == "60" and "did" in parts[1]:
        dup_line_idx = i
        print(f"Duplicate line at index {i}: {line[:80]}")
        break

if dup_line_idx is None:
    print("ERROR: duplicate not found")
    exit(1)

# Remove the duplicate line
lines.pop(dup_line_idx)
# end_246 shifts by 1 (the blank line is now one earlier)
end_246 -= 1

# Renumber tokens 61-110 -> 60-109 in the sentence range, also update HEAD refs
# But we also need to update all HEAD values that reference tokens >= 61
# Specifically within sent_246 only

# First pass: renumber token IDs >= 61 and update HEAD values
# Token renaming map: old_id -> new_id for tokens 61-110
rename = {}
for old in range(61, 111):
    rename[old] = old - 1

for i in range(start_246, end_246):
    line = lines[i].rstrip()
    if not line or line.startswith("#"):
        continue
    parts = line.split("\t")
    if len(parts) < 8:
        continue
    tok_id_str = parts[0]
    if not tok_id_str.isdigit():
        continue
    tok_id = int(tok_id_str)
    head_str = parts[6]

    new_tok_id = rename.get(tok_id, tok_id)
    new_head = rename.get(int(head_str), int(head_str)) if head_str.isdigit() else head_str

    parts[0] = str(new_tok_id)
    parts[6] = str(new_head)
    lines[i] = "\t".join(parts) + "\n"

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Fixed sent_246. Verifying token count...")

import re
def count_token_rows(fp):
    count = 0
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line and not line.startswith("#"):
                parts = line.split("\t")
                if len(parts) >= 2 and re.match(r"^\d+$", parts[0]):
                    count += 1
    return count

sk = r"c:/Users/bibleman/repos/readers-bofm/data/parses/llm-direct/3nephi-batches/skeleton-10.conllu"
fl = filepath
print(f"skeleton-10 tokens: {count_token_rows(sk)}")
print(f"filled-10   tokens: {count_token_rows(fl)}")
