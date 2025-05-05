# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "libcst",
# ]
# ///
import os
from typing import List, Self
import libcst as cst


class ProjectVisitor(cst.CSTVisitor):
    def __init__(self: Self, module: cst.Module,  input_file: str, output_file: str) -> None:
        self.module: cst.Module = module
        self.input_file: str = input_file
        self.output_file: str = output_file

        self.in_file_separator: str = "-" * 50
        self.out_file_separator: str = "+" * 50

        super().__init__()

    def visit_Module(self: Self, node: cst.Module) -> bool | None:
       with open(self.output_file, "a") as f:
        f.write(f"\n{self.out_file_separator}\n\nCurrent file: {self.input_file}\n\n")

        return super().visit_Module(node)
    
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
        class_definition: str = f"class {class_name}{("(" + ",".join(super_class_names) + ")") if len(super_class_names) >= 1 else ""}:"

        with open(self.output_file, "a") as f:
            f.write(
                f"{self.in_file_separator}\n\n{class_definition}\n\n"
            )

        return super().visit_ClassDef(node)

    def leave_ClassDef(self: Self, original_node: cst.ClassDef) -> None:
        with open(self.output_file, "a") as f:
            f.write(f"{self.in_file_separator}\n\n")
        
        return super().leave_ClassDef(original_node)

    def visit_FunctionDef(self: Self, node: cst.FunctionDef) -> bool | None:
        function_name: str = node.name.value

        if function_name.startswith("_") or function_name.startswith("__"):
            return

        function_definition: str = f"def {function_name}({self.module.code_for_node(node.params)})"
        if node.returns is not None:
            function_return: str = self.module.code_for_node(node.returns.annotation)
            function_definition += f" -> {function_return}:"
        else:
            function_definition += ":"
        
        with open(self.output_file, "a") as f:
            f.write(f"{function_definition}\n")

        return super().visit_FunctionDef_params(node)


DOCS_FILE: str = "manim_docs.txt"
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
            code_module.visit(ProjectVisitor(module=code_module, input_file=current_file, output_file=DOCS_FILE))
