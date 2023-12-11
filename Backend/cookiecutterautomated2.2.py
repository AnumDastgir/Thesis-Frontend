#This code saves Models with the models tag and saves the script into the models directory in case 
#the models foler doesn't exist already.
#Also adds Visualizations to visualization folder ==Shud exactly put visualization
# Enter destination directory: /000.Thesis 1/Testing 2.0/thesis_testing2.0repo/src/testCookiecutterAutomated2.2f2
#/000.Thesis 1/Testing 2.0/thesis_testing2.0repo/src/testCookiecutterAutomated2.2f2/Notebook1Rope/17.oct.2023Testing/Comparison
#Have used Rope package to refactor. Not much refactoring is done but
#is used to rename variables(cookiecutterautomated2.2old.py)
#refactored version of code with modularization, use of constants, error handling, and.. 
#separation of concerns (each function or class has a single responsibility and doesn't do too much. For example,..
#the code for generating scripts could be separated from the code for reading notebooks and handling file operations)

#Setup activity contains all imports= sorted and imports shouldn't be repeated but imports must be tagged properly.

#Now adding Heuristics
#-1 Cells with multiple tags will generate only 1 script with 1st tag
#-2 Merging 3 scripts if they have same names consecutively try 2
#-3 Merging all with similar names consecutively try 2,

#Trying to add refactoring= tricky cuz i need to discover global variables etc. Models need tags


import tkinter as tk
from tkinter import filedialog
import json
import os
import subprocess
from rope.base import libutils
from rope.refactor import rename
import re

# Constants
SKIP_TAGS = [""]
REQUIREMENTS_KEYWORD = "pip install"

def write_file(name, content, append=False):
    """Write content to a file."""
    mode = "a" if append else "w"
    try:
        with open(name, mode) as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to {name}: {e}")

def read_notebook(file_path):
    """Read a Jupyter notebook file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            source = file.read()
        return json.loads(source)
    except Exception as e:
        print(f"Error reading notebook file: {e}")
        return None

def should_skip_tag(tag):
    """Check if a tag should be skipped."""
    return tag.lower() in SKIP_TAGS

def tag_contains_keyword(tag, keyword):
    """Check if a tag contains a specific keyword."""
    return keyword.lower() in tag.lower()

def fetch_tags(code):
    """Fetch tags from code cells."""
    tags_dict = {}
    cell_sequence = 1
    tag_count = 0
    for cell in code['cells']:
        if cell['cell_type'] == "code" and "tags" in cell['metadata']:
            tags = cell['metadata']['tags']
            tag_count += len(tags)
            for tag in tags:
                lowercase_tag = tag.lower()
                if lowercase_tag == "models":
                    print(f"Found a 'models' tag in cell {cell_sequence}")
                if not should_skip_tag(lowercase_tag):
                    if lowercase_tag in tags_dict:
                        tags_dict[lowercase_tag].append((cell, cell_sequence))
                    else:
                        tags_dict[lowercase_tag] = [(cell, cell_sequence)]
        cell_sequence += 1
    print("Total number of tags read:", tag_count)
    return tags_dict

def merge_and_generate_scripts(tags_dict, code_cells):
    """Merge consecutive scripts with the same name, add comments, and rename."""
    merged_scripts = {}
    current_script = None
    current_script_name = None
    current_script_sequence = None
    comment_tags = []

    for cell in code_cells:
        if cell['cell_type'] == "code":
            tags = cell['metadata']['tags'] if "tags" in cell['metadata'] else []

            # Handle multiple tags for a single cell
            if len(tags) > 1:
                comment_tags.append("# Tags: " + ", ".join(tags))

            lowercase_tags = [tag.lower() for tag in tags if not should_skip_tag(tag)]
            script_name = "_".join(lowercase_tags)  # Use concatenated tags as the script name
            cell_sequence = cell['metadata']['cell_sequence']

            # If the cell has the "checkpoint activity" tag, append its code to the previous script
            if "checkpoint activity" in tags:
                if current_script:
                    current_script += '\n'.join(cell['source']) + '\n'
            else:
                if current_script_name == script_name:
                    # Continue merging
                    current_script += '\n'.join(cell['source']) + '\n'
                else:
                    if current_script:
                        # Save the merged script
                        merged_scripts[current_script_sequence] = {
                            "script_name": current_script_name,
                            "script_content": current_script,
                            "comment_tags": comment_tags,
                        }

                    current_script = '\n'.join(cell['source']) + '\n'
                    current_script_name = script_name
                    current_script_sequence = cell_sequence
                    comment_tags = []

    # Save the last merged script
    if current_script:
        merged_scripts[current_script_sequence] = {
            "script_name": current_script_name,
            "script_content": current_script,
            "comment_tags": comment_tags,
        }

    # Generate scripts from merged data
    scripts = {}
    for sequence, script_data in merged_scripts.items():
        script_name = script_data['script_name']
        script_content = script_data['script_content']
        comment_tags = script_data['comment_tags']

        # Check if there are consecutive scripts with the same name
        if sequence - 1 in merged_scripts:
            previous_script_name = merged_scripts[sequence - 1]['script_name']
            if previous_script_name == script_name:
                script_name = f"{sequence - 1}_{script_name}"
                comment_tags.append(f"Merged '{sequence - 1}_{previous_script_name}'")

        if comment_tags:
            script_content = '\n'.join(comment_tags) + '\n' + script_content
        scripts[script_name] = script_content

    return scripts


def extract_requirements(code):
    """Extract requirements from code."""
    requirements = set()
    lines = code.split('\n')
    for line in lines:
        if line.startswith("#"):
            continue
        if REQUIREMENTS_KEYWORD in line:
            requirement = line.split(REQUIREMENTS_KEYWORD)[1].strip()
            requirements.add(requirement)
    return requirements

def extract_current_requirements():
    """Extract requirements from the current environment using 'pip list'."""
    try:
        process = subprocess.Popen(['pip', 'list', '--format=freeze'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        requirements_list = output.decode("utf-8").strip().split('\n')
        return requirements_list
    except Exception as e:
        print(f"Error extracting current environment requirements: {e}")
        return []

def write_current_requirements(requirements_list, requirements_file):
    """Write current environment requirements to requirements.txt."""
    try:
        with open(requirements_file, 'w') as f:
            for requirement in requirements_list:
                f.write(requirement + '\n')
    except Exception as e:
        print(f"Error writing current environment requirements to {requirements_file}: {e}")

def exports_model(code):
    """Check if a code cell exports a model."""
    return any(keyword in code for keyword in ["model.save(", "torch.save(", "joblib.dump("])

def rename_variable(file_path, old_name, new_name):
    """Rename a variable using rope."""
    try:
        project = rope.base.project.Project('.')
        pycore = project.pycore
        resource = libutils.path_to_resource(file_path, pycore)
        ast = resource.get_object()

        renamer = rename.Renamer(project, ast)
        changes = renamer.rename(old_name, new_name)
        changes.do()
    except Exception as e:
        print(f"Error renaming variable: {e}")

def extract_imports(code):
    """Extract import statements from code."""
    import_statements = re.findall(r'^\s*import\s+\S+.*$', code, re.MULTILINE)
    from_statements = re.findall(r'^\s*from\s+\S+\s+import\s+\S+.*$', code, re.MULTILINE)
    import_statements.extend(from_statements)
    return import_statements

def main():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Jupyter Notebook",
        filetypes=[("Jupyter Notebook Files", "*.ipynb")]
    )

    if file_path:
        print("Selected file:", file_path)
        code = read_notebook(file_path)
        if code:
            code_cells = code['cells']
            
            for i, cell in enumerate(code_cells, 1):
                cell['metadata']['cell_sequence'] = i

            tags_dict = fetch_tags(code)
            scripts = merge_and_generate_scripts(tags_dict, code_cells)

            destination_directory = input("Enter the destination directory: ")

            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)

            models_directory = os.path.join(destination_directory, "models")
            if not os.path.exists(models_directory):
                os.makedirs(models_directory)

            visualization_directory = os.path.join(destination_directory, "visualization")
            if not os.path.exists(visualization_directory):
                os.makedirs(visualization_directory)

            data_directory = os.path.join(destination_directory, "data")
            if not os.path.exists(data_directory):
                os.makedirs(data_directory)

            setup_activity = []  # List to store setup activity code
            setup_activity_imports = []  # List to store setup activity import statements

            script_files = []
            for tag, code in scripts.items():
                script_file = f"{tag}.py"
                target_directory = models_directory if tag_contains_keyword(tag, "models") else destination_directory
                
                if tag_contains_keyword(tag, "data visualization phase"):
                    target_directory = visualization_directory
                
                if tag_contains_keyword(tag, "data pre-processing") or tag_contains_keyword(tag, "data ingestion"):
                    target_directory = data_directory

                target_path = os.path.join(target_directory, script_file)

                if os.path.exists(target_path):
                    with open(target_path, 'r') as f:
                        existing_content = f.read()

                    if code not in existing_content:
                        code = existing_content + '\n' + code

                script_content = code

                if tag_contains_keyword(tag, "setup activity"):
                    setup_activity.append(script_content)  # Add to setup activity code
                    # Extract import statements and add them to setup_activity_imports
                    setup_activity_imports.extend(extract_imports(script_content))
                else:
                    write_file(target_path, script_content, append=True)  # Append to existing file

                script_files.append(script_file)
                print(f"Generated file {script_file}")

            # Write setup activity code to "setup_activity.py" script
            setup_activity_code = '\n'.join(setup_activity)
            setup_activity_file = os.path.join(destination_directory, "setup_activity.py")

            # Check if setup activity file exists
            if not os.path.exists(setup_activity_file):
                # Create the setup activity file if it doesn't exist
                write_file(setup_activity_file, setup_activity_code, append=False)
            else:
                # Append the setup activity code if the file exists
                with open(setup_activity_file, 'a') as f:
                    f.write(setup_activity_code)

            requirements = set()
            for code in scripts.values():
                requirements.update(extract_requirements(code))

            requirements_content = '\n'.join(sorted(requirements))
            requirements_file = os.path.join(destination_directory, "requirements.txt")
            write_file(requirements_file, requirements_content)
            print("Generated requirements.txt file at {}".format(requirements_file))

            current_requirements = extract_current_requirements()
            write_current_requirements(current_requirements, requirements_file)

            # Save the import statements in the setup activity script
            if setup_activity_imports:
                setup_activity_imports = list(set(setup_activity_imports))  # Remove duplicates
                setup_activity_imports = '\n'.join(setup_activity_imports) + '\n'
                with open(setup_activity_file, 'a') as f:
                    f.write(setup_activity_imports)

            print("All files moved and scripts executed successfully.")
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()

