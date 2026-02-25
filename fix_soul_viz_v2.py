import sys

file_path = "project-genesis/skills/soul-evolution/tools/soul-viz.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Patch start
for i, line in enumerate(lines):
    if 'return f"""<!DOCTYPE html>' in line:
        lines[i] = '    html = """<!DOCTYPE html>
'
        print(f"Patched start at line {i+1}")

# Patch end
# We need to insert lines, so we iterate backwards to not mess up indices
for i in range(len(lines) - 1, -1, -1):
    if '</html>"""' in lines[i]:
        # Add the return statement after this line
        lines[i] = '</html>"""
'
        lines.insert(i + 1, '    return html.replace("{data_json}", data_json).replace("{{", "{").replace("}}", "}")
')
        print(f"Patched end at line {i+1}")

with open(file_path, "w") as f:
    f.writelines(lines)

print("soul-viz.py patched successfully (ALL occurrences).")
