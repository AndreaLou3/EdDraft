import yaml
import importlib
from edapi import EdAPI
from pathlib import Path
from utils import get_all_assignments

configs_folder = Path("configs")

# Authentication
ed = EdAPI()
ed.login()
user_info = ed.get_user_info()
user = user_info["user"]

# cs61c test = 61031
# cs61c sp26 = 93340
course_config = {
    "course_id": 61031,
    "post_privately": True
}

# ask for assignment and verify
all_assignments = get_all_assignments()
assignment_id = input("Assignment Name (e.g. Project_3/Midterm/Final):").strip()

if assignment_id not in all_assignments:
    print(f"Error: Assignment '{assignment_id}' is not currently supported.")
    print(f"Available assignments: {', '.join(all_assignments.keys())}")
    exit(1)

assignment_config = all_assignments[assignment_id]

# config should provide path to corresponding logic posting module
logic_module_path = assignment_config.get("logic_module")
if not logic_module_path:
    print(f"Error: No logic module specified in config for '{assignment_id}'")
    exit(1)
logic_module_name = logic_module_path.replace(".py", "").replace("/", ".")

try:
    logic_module = importlib.import_module(logic_module_name)
except ModuleNotFoundError as e:
    print(f"Error: Could not import logic module '{logic_module_name}': {e}")
    exit(1)

# expect each logic module to implement post_assignment(ed, assignment_config, course_config)
if not hasattr(logic_module, "post_assignment"):
    print(f"Error: Logic module '{logic_module_name}' does not implement 'post_assignment' function")
    exit(1)

logic_module.post_assignment(
    ed=ed,
    assignment_config=assignment_config,
    course_config=course_config
)