import ast, black

class FromImportNodeTransformer(ast.NodeTransformer):
    def __init__(self, file_names):
        self.from_imports = dict()
        self.file_names = file_names
        self.module_set = set()

    def visit_ImportFrom(self, node):
        module = node.module
        level = node.level

        if module in self.file_names:
            return

        imported_names = set()

        for alias in node.names:
            imported_names.add(
                (
                    alias.name,
                    alias.asname
                )
            )

        if module in self.module_set:
            self.from_imports[module]["names"].update(imported_names)
            return

        self.module_set.add(module)

        self.from_imports[module] = {
            "module": module,
            "level": level,
            "names": imported_names,
        }

# ----------------------------------------------------------------

files = (
    "util.py",
    "ui.py",
    "kt.py",
    "expand.py",
    "tool.py",
    "main.py"
)

file_names = [n.rstrip(".py") for n in files]

output = "start.py"
seq = "\n\n"

codes = list()
for name in files:
    with open(name, mode="r", encoding="utf-8") as f:
        text = f.read()
        codes.append(text)

code = seq.join(codes)

# ----------------------------------------------------------------

tree = ast.parse(code)
transformer = FromImportNodeTransformer(file_names)
transformer.visit(tree)

imports = sorted(transformer.from_imports.items(), key=lambda x: len(x[0]), reverse=True)

for key, item in imports:
    module = item["module"]
    level = item["level"]
    names = list(item["names"])

    aliases = list()
    for alias in names:
        aliases.append(
            ast.alias(*alias)
        )

    import_node = ast.ImportFrom(
        module=module,
        names=aliases,
        level=level
    )

    tree.body.insert(0, import_node)

ast.fix_missing_locations(tree)

# ----------------------------------------------------------------

code = ast.unparse(tree)
header = f"# Auto-generated {output} by bud.py\n# Source files: {', '.join(files)}\n\n" 
code = black.format_str(header + code, mode=black.Mode())

with open(output, mode="w", encoding="utf-8") as f:
    f.write(code)