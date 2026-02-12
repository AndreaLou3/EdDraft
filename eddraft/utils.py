from pathlib import Path
import yaml
from typing import Dict, Any

def get_all_assignments(config_root: str = "configs") -> Dict[str, Dict[str, Any]]:
    """
    Recursively reads all YAML files in the given folder and returns a dictionary
    mapping assignment names to their full configuration dictionary.
    """
    config_path = Path(config_root)
    assignments: Dict[str, Dict[str, Any]] = {}

    for yaml_file in config_path.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if isinstance(data, dict):
                # Merge all assignments in this YAML file
                for assignment_name, config in data.items():
                    if assignment_name in assignments:
                        print(f"Warning: Duplicate assignment '{assignment_name}' in {yaml_file}")
                    assignments[assignment_name] = config

        except Exception as e:
            print(f"Warning: Could not read {yaml_file}: {e}")

    return dict(sorted(assignments.items()))
