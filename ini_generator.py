import os
import ast
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_top_level_definitions(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read(), filename=file_path)
    top_level_functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
    top_level_classes = [node.name for node in tree.body if isinstance(node, ast.ClassDef)]
    top_level_globals = [node.targets[0].id for node in tree.body if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)]
    return top_level_functions, top_level_classes, top_level_globals

def create_import_statements(definitions_dict):
    import_statements = []
    all_exports = []
    
    for module, definitions in definitions_dict.items():
        module_name = os.path.basename(module).replace(".py", "")
        functions, classes, globals = definitions
        if functions or classes or globals:
            import_statement = f"from .{module_name} import (\n"
            for func in functions:
                import_statement += f"    {func},\n"
                all_exports.append(func)
            for cls in classes:
                import_statement += f"    {cls},\n"
                all_exports.append(cls)
            for global_var in globals:
                import_statement += f"    {global_var},\n"
                all_exports.append(global_var)
            import_statement += ")\n"
            import_statements.append(import_statement)
    
    return import_statements, all_exports

def write_init(definitions_dict, output_folder):
    import_statements, all_exports = create_import_statements(definitions_dict)
    
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
        logging.info(f"Processing file: {file}")
        functions, classes, globals = extract_top_level_definitions(file)
        if functions or classes or globals:
            definitions_dict[file] = (functions, classes, globals)
    return definitions_dict

# Get the current script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# List all .py files in the current directory
files = [str(file) for file in Path(script_dir).glob("*.py") if file.name != "__init__.py" and file.name != os.path.basename(__file__)]

# Process files and write the __init__.py file
definitions_dict = process_files(files)
write_init(definitions_dict, script_dir)

logging.info("Finished generating __init__.py")
