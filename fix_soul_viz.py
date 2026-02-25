import sys

file_path = "project-genesis/skills/soul-evolution/tools/soul-viz.py"

with open(file_path, "r") as f:
    lines = f.readlines()

# Patch start
for i, line in enumerate(lines):
    if 'return f"""<!DOCTYPE html>' in line:
        lines[i] = '    html = """<!DOCTYPE html>\n'
        print(f"Patched start at line {i+1}")
        break

# Patch end
for i, line in enumerate(lines):
    if '</html>"""' in line:
        lines[i] = '</html>"""\n'
        lines.insert(i + 1, '    return html.replace("{data_json}", data_json).replace("{{", "{").replace("}}", "}")\n')
        print(f"Patched end at line {i+1}")
        break

with open(file_path, "w") as f:
    f.writelines(lines)

print("soul-viz.py patched successfully.")
