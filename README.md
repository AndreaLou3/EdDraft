# EdDraft

Tool for templating and drafting EdStem threads

### Requirements

- [edapi](https://github.com/smartspot2/edapi) >=0.1.0
- [Jinja2](https://jinja.palletsprojects.com/en/stable/) >=3.1.6

### Setup

1. Install dependencies
    ```js
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e .
    ```

### How It Works

Each assignment type needs three things:

1. **A config file** — defines the assignment's data (due dates, spec URL, etc.) and points to the logic module and templates to use
2. **A logic module** — a Python file with a `post_assignment` function that defines the posting sequence (what threads to create, in what order), any other special logic you'd like
3. **Templates** — Jinja XML files that define the content of each post for that assignment type

This means different assignment types (projects, labs, homework) can have completely different posting logic and templates, while sharing the same runner and utilities.

## Quickstart

If you're posting based on an existing template:
- Run `python3 main.py`, input the desired assignment name (e.g. Project_3/Midterm/Final)

### Adding a New Assignment of an existing type

Add an entry to a config file (Example below):
```yaml
# configs/project_configs.yaml

Project_2:
  name: "Project 2"
  project_num: "2"
  part_a_due: "February 26th, 11:59 PST"
  part_b_due: "March 5th, 11:59 PST"
  ab_cutoff: 6
  spec_url: "https://cs61c.org/sp26/projects/proj2/"
  subthreads:
    - "Absolute Value (Walkthrough)"
    - "RELU"
    - "Argmax"
    - "Dot Product"
  logic_module: "logic.project_posting"   # points to logic/project_posting.py
  template_folder: "templates/projects"   # points to your assignment templates
```

The `logic_module` and `template_folder` fields tell the runner where to find your logic and templates. All other fields are passed directly to your templates and logic module as variables.

If your assignment type logic already exists, just fill in the config and run. The expected format of the assignment config depends on the logic module, and is described at the top of the file (see `logic.project_posting`).

### Creating a New Assignment Type

You need to create two things before adding assignment configs: a logic module and a set of templates.

Logic Module: Create a file at `logic/your_assignment_type.py` with a `post_assignment` function

The function should recieve three arguments:

| Argument | Type | Description |
|---|---|---|
| `ed` | `EdAPI` | Authenticated Ed API client |
| `assignment_config` | `dict` | The full config entry for this assignment, including all the custom fields |
| `course_config` | `dict` | Course-level settings like `course_id` and `post_privately` |

Templates: Create templates in your `template_folder`. Templates are standard XML with Jinja expressions — all fields from your assignment config are available as variables.

```xml
<?xml version="1.0" encoding="utf-8"?>
<document version="2.0">
  <paragraph>
    Homework {{ hw_num }} is released! It is due <bold>{{ due_date }}</bold>.
  </paragraph>
  <paragraph>
    Spec: <link href="{{ spec_url }}">link</link>
  </paragraph>
</document>
```

The `to_edstem` utility strips all formatting whitespace/newlines before sending to Ed to match their expected format.

## Utilities

These are available to all logic modules:

`to_edstem(template, **kwargs)`
Renders a Jinja template and transforms the output into Ed's XML format. Strips all newlines and indentation, and maps readable tag names to Ed's equivalents.

```python
content = to_edstem(env.get_template("my_template.xml.jinja"), **assignment_config)
```

`create_ed_environment(template_folder)`
Creates a Jinja environment configured for Ed XML templates.

```python
env = create_ed_environment(assignment_config["template_folder"])
template = env.get_template("my_template.xml.jinja")
```

### Misc

Good to know when running ed.post_thread():
- More info on edapi here: https://github.com/smartspot2/edapi

| Parameter | Default | Description |
|---|---|---|
| `subcategory` | `""` | Ed subcategory |
| `subsubcategory` | `""` | Ed sub-subcategory |
| `is_pinned` | `False` | Pin the post |
| `is_private` | `True` | Visible to staff only |
| `is_megathread` | `False` | Enable megathread mode |

## Sample Structure

```
├── configs/
│   └── project_configs.yaml     # Project configs
├── logic/
│   ├── __init__.py
│   ├── logic_utils.py           # Shared utilities
│   └── project_posting.py       # Logic module for projects
└── templates/
    └── projects/
        ├── project_megathread_template.xml.jinja
        ├── project_partnering_template.xml.jinja
        └── project_subthread_template.xml.jinja
```