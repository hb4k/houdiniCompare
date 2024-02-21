import os
import json
import hou
import tkinter as tk
from tkinter import filedialog


def get_source_path():
    # create window
    root = tk.Tk()
    root.withdraw()  # Hide main window

    # show window to select file
    file_path = filedialog.askopenfilename(title="Select source to compare")

    # Check if a file was selected
    if file_path:
        print(f'Source file = {file_path}')
    else:
        print('Not selected any file')

    return file_path

    root.destroy()

def get_info_node(node):
    info = {}
    info['name'] = node.name()
    info['type'] = node.type().name()
    info['path'] = node.path()
    info['parms'] = {}

    for parm in node.parms():
        # Exclude the Ramp parameter
        if parm.parmTemplate().type() == hou.parmTemplateType.Ramp:
            continue
        info['parms'][parm.name()] = parm.eval()

    for input_node in node.inputs():
        if input_node is not None:
            info['inputs_nodes'] = input_node.path()
        else:
            print(f"Warning: Input node for {node.path()} is None")

    if node.isLockedHDA() is not True:
        if node.children():
            info['children'] = []
            for child in node.children():
                child_info = get_info_node(child)
                if child_info:
                    info['children'].append(child_info)
                else:
                    print(f"Warning: Child node info is None for {child.path()}")
                    break

    return info


def hip_to_json(hip_path):
    name, ext = os.path.splitext(hip_path)
    path = name + '.json'

    return path            
    
def current():
    scene_info = []
    obj = hou.node('/obj')
    
    print("Fetching scene data")
    
    for node in obj.children():
        scene_info.append(get_info_node(node))

    print("Data Collect Successfully!")

    # print(scene_info)
    
    return scene_info

def create_source():

    obj = hou.node('/obj')

    source_path = get_source_path()
    current_scene_path = hou.hipFile.name()

    print("Saving current scene...")
    hou.hipFile.save(current_scene_path)
    print("Current scene saved at: " + current_scene_path)

    print("Opening source file...")

    hou.hipFile.load(source_path)

    source_scene_info = []


    print("Exporting source file to json...")
    
    for node in obj.children():
        source_scene_info.append(get_info_node(node))

    print("Saving source file...")

    json_source = hip_to_json(source_path)

    with open(json_source, 'w') as json_file:
        json.dump(source_scene_info, json_file, indent=4)

    print("Source exported successfully at: " + json_source)

    print("Opening current scene...")
    hou.hipFile.load(current_scene_path)

    return json_source

    message = "Backup created successfully! at: " + json_source + "\n\n"

    hou.ui.displayMessage(message, title="Popup Message", buttons=("OK",))

def select_source():
    message = "Select the source file to compare:"

    file_path = hou.ui.selectFile(title="Select source to compare", file_type=hou.fileType.Any, pattern="*.json")

    if file_path:
        print(f'Source file = {file_path}')
    else:
        print('Not selected any file')

    if '$HIP' in file_path:
        file_path = file_path.replace('$HIP', hou.text.expandString('$HIP'))

    return file_path

def welcome():
    message = """
    Welcome to Houdini Compare Tool!!
    Please select an option:
    """
    buttons = ("Create Source", "Select Source", "Cancel") 

    selection = hou.ui.displayMessage(message, buttons=buttons, close_choice=3)

    if selection == 0:
        source = create_source()
    elif selection == 1:
        source = select_source()
    else:
        source = None

    return source

def comment(node, comment):
    existing_comment = node.comment()
    new_comment = existing_comment + "\n" + comment
    node.setComment(new_comment)
    node.setGenericFlag(hou.nodeFlag.DisplayComment,True)


def get_json(path):
    try:
        with open(path, 'r') as json_file:
            json_data = json.load(json_file)
        return json_data
    
    except Exception as e:

        print(f"Error loading JSON data from {path}: {e}")
        return None


def get_node_info(node_list, node_path):
    for node_info in node_list:
        if node_info['path'] == node_path:
            return node_info
    return None

def compare_and_mark_differences(scene_data, json_data):
    # Iterate over the scene data and compare it with the JSON data
    for scene_node_info in scene_data:
        scene_node_path = scene_node_info['path']
        json_node_info = get_node_info(json_data, scene_node_path)

        if json_node_info is None:
            print(f"Node {scene_node_path} does not exist in the JSON data")
            node = hou.node(scene_node_path)
            node.setColor(hou.Color((1, 0, 0)))  # Change the node color to red
            comment(node, "This node doesnt exist in source scene")
            continue

        # Compare the node parameters
        scene_parms = scene_node_info['parms']
        json_parms = json_node_info['parms']

        for parm_name, parm_value in scene_parms.items():
            if parm_name not in json_parms:
                
                print(f"Node {scene_node_path} has parameter {parm_name} that does not exist in the JSON data")
                
                continue

            json_parm_value = json_parms[parm_name]

            print("scene node",scene_node_info['name'],"parm_name", parm_name,"parm_value", parm_value, "json_parm_value", json_parm_value)

            if parm_value != json_parm_value:
                print(f"Node {scene_node_path} has different value for parameter {parm_name}")
                target_node = hou.node(scene_node_path)
                print("target_node")

                if target_node:
                    target_node.setColor(hou.Color((0, 0, 1)))  # Change the node color to BLUE
                    comment_text = f"the parm {parm_name} was {json_parm_value} and now is {parm_value}"
                    comment(target_node, comment_text)
                

                

        # Compare the node type
        scene_node_type = scene_node_info['type']
        json_node_type = json_node_info['type']

        if scene_node_type != json_node_type:
            target_node = hou.node(scene_node_path)
            if target_node:
                target_node.setColor(hou.Color((1, 0, 0)))  # Change the node color to red

        # Recursively compare the information of the children of the current node
        scene_children = scene_node_info.get('children', [])
        json_children = json_node_info.get('children', [])

        compare_and_mark_differences(scene_children, json_children)

# Example usage
def main():
    # Load scene data and JSON data
    json_file_path = welcome()
    scene_data = current()
    
    
    # Load JSON data from the file path
    json_data = get_json(json_file_path)
    
    if json_data:
        print(f"JSON data loaded from {json_file_path}")
        # Compare scene data with JSON data and mark differences
        compare_and_mark_differences(scene_data, json_data)


main()
