# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "libcst",
# ]
# ///
import os
from typing import Self
import libcst as cst

class ProjectVisitor(cst.CSTVisitor):
    def __init__(self: Self, output_file: str) -> None:
        self.output_file = output_file
        
        super().__init__()

    
    def visit_ClassDef(self, node) -> bool | None:
        class_name: str = node.name.value

        if class_name.startswith("_"):
            return

        super_class_names = [base.value.value for base in node.bases]
        super_class_names = [name if isinstance(name, str) else name.value for name in super_class_names]

        with open(self.output_file, "a") as f:
            inherit_string: str = f"inherit(s) from: {",".join(super_class_names)}" if len(super_class_names) >= 1 else "doesn't inherit from any class."
            f.write(
                f"The name of the class: {class_name}, and this class {inherit_string}\n\n"
            )

        return super().visit_ClassDef(node)

DOCS_FILE = "manim_docs.txt"
if True:
    with open(DOCS_FILE, "w") as f:
        f.close()

for directory_path, _, file_names in os.walk("manimlib"):
    for file_name in file_names:
        current_file: str = os.path.join(directory_path, file_name)
        if not current_file.endswith("py") or current_file.endswith("__init__.py"):
            continue

        with open(current_file) as f:
            code: cst.Module = cst.parse_module(f.read())
            code.visit(ProjectVisitor(output_file=DOCS_FILE))
            