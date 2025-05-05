# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "libcst",
# ]
# ///
import os
from typing import List, Self
import libcst as cst
from libcst.display import dump


class ProjectVisitor(cst.CSTVisitor):
    def __init__(self: Self, module: cst.Module,  output_file: str) -> None:
        self.output_file: str = output_file
        self.module: cst.Module = module
        self.separator: str = "-" * 50
        super().__init__()

    def visit_ClassDef(self: Self, node: cst.ClassDef) -> bool | None:
        class_name: str = node.name.value

        if class_name.startswith("_"):
            return

        super_class_names: List[str | cst.Name] = [
            base.value.value for base in node.bases
        ]
        super_class_names: List[str] = [
            name if isinstance(name, str) else name.value for name in super_class_names
        ]

        with open(self.output_file, "a") as f:
            inherit_string: str = (
                f"inherit(s) from: {','.join(super_class_names)}"
                if len(super_class_names) >= 1
                else "doesn't inherit from any class."
            )
            f.write(
                f"{self.separator}\n\nThe name of the class: {class_name}, and this class {inherit_string}\n\n"
            )

        return super().visit_ClassDef(node)

    def leave_ClassDef(self: Self, original_node: cst.ClassDef) -> None:
        with open(self.output_file, "a") as f:
            f.write(f"{self.separator}\n\n")
        
        return super().leave_ClassDef(original_node)

    def visit_FunctionDef(self: Self, node: cst.FunctionDef) -> bool | None:
        function_name: str = node.name.value

        if function_name.startswith("_") or function_name.startswith("__"):
            return

        function_definition = f"def {function_name}({self.module.code_for_node(node.params)})"
        if node.returns is not None:
            function_return = self.module.code_for_node(node.returns.annotation)
            function_definition += f" -> {function_return}"
        
        with open(self.output_file, "a") as f:
            f.write(f"{function_definition}\n")

        return super().visit_FunctionDef_params(node)


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
            code_module: cst.Module = cst.parse_module(f.read())
            code_module.visit(ProjectVisitor(code_module, output_file=DOCS_FILE))
