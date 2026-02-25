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
for i in range(len(lines) - 1, -1, -1):
    if '</html>"""' in lines[i]:
        # Only patch if not already patched
        if i + 1 >= len(lines) or 'return html.replace' not in lines[i+1]:
            lines[i] = '</html>"""
'
            lines.insert(i + 1, '    return html.replace("{data_json}", data_json).replace("{{", "{").replace("}}", "}")
')
            print(f"Patched end at line {i+1}")

with open(file_path, "w") as f:
    f.writelines(lines)

print("soul-viz.py patched successfully.")
