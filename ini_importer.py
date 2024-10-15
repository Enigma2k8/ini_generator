import os
import ast
import configparser
from pathlib import Path

def extract_top_level_definitions(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)
    top_level_functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    top_level_classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    return top_level_functions, top_level_classes

def create_import_statements(definitions_dict, globals_dict):
    import_statements = []
    all_exports = []
    
    for module, definitions in definitions_dict.items():
        module_name = os.path.basename(module).replace(".py", "")
        functions, classes = definitions
        if functions or classes:
            import_statement = f"from .{module_name} import (\n"
            for func in functions:
                import_statement += f"    {func},\n"
                all_exports.append(func)
            for cls in classes:
                import_statement += f"    {cls},\n"
                all_exports.append(cls)
            if module_name in globals_dict:
                for global_var in globals_dict[module_name]:
                    import_statement += f"    {global_var},\n"
                    all_exports.append(global_var)
            import_statement += ")\n"
            import_statements.append(import_statement)
    
    return import_statements, all_exports

def write_init(definitions_dict, globals_dict, output_folder):
    import_statements, all_exports = create_import_statements(definitions_dict, globals_dict)
    
    init_file_path = os.path.join(output_folder, '__init__.py')
    
    with open(init_file_path, 'w') as file:
        for statement in import_statements:
            file.write(statement)
        file.write("\n__all__ = [\n")
        for item in all_exports:
            file.write(f"    '{item}',\n")
        file.write("]\n")

def process_files(files):
    definitions_dict = {}
    for file in files:
        functions, classes = extract_top_level_definitions(file)
        if functions or classes:
            definitions_dict[file] = (functions, classes)
    return definitions_dict

# Adjust the script to handle relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
files = [
    os.path.join(script_dir, ".py")
]

# Dictionary of globals to be included from specific modules
globals_dict = {
    "": [""],  # Add other globals as needed
}

# Process files and write the __init__.py file
definitions_dict = process_files(files)
write_init(definitions_dict, globals_dict, script_dir)
