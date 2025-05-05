# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "libcst",
# ]
# ///
import os
import libcst as cst

class ProjectVisitor(cst.CSTVisitor):
    def visit_ClassDef(self, node) -> bool | None:
        class_name = node.name.value
        super_class_names = [base.value.value for base in node.bases]
        super_class_names = [name if isinstance(name, str) else name.value for name in super_class_names]

        return super().visit_ClassDef(node)

for directory_path, _, file_names in os.walk("manimlib"):
    for file_name in file_names:
        current_file: str = os.path.join(directory_path, file_name)
        if not current_file.endswith("py") or current_file.endswith("__init__.py"):
            continue

        with open(current_file) as f:
            code: cst.Module = cst.parse_module(f.read())
            code.visit(ProjectVisitor())
            