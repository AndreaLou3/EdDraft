from jinja2 import Environment, FileSystemLoader, select_autoescape
from edapi import EdAPI
from pathlib import Path
from typing import Dict, Any, List
from .logic_utils import to_edstem, create_ed_environment


def post_assignment(ed: EdAPI, assignment_config: Dict[str, Any], course_config: Dict[str, Any]):
    """
    post project threads using the provided configs
    
    expecting assignment_config to look like:
        - name: str
        - project_num: str
        - part_a_due: str
        - part_b_due: str
        - ab_cutoff: int
        - spec_url: str
        - num_subthreads: int
        - subthreads: List[str]
        - logic_module: "logic.project_posting"
        - template_folder: str (path to Jinja templates)
    """
    course_id = course_config["course_id"]
    post_privately = course_config.get("post_privately", True)

    # useful vars for pretty titles
    project_name = assignment_config["name"]
    project_num = assignment_config["project_num"]
    bracketed_name = f"[Project {project_num}]"

    env = create_ed_environment(assignment_config["template_folder"])

    # partner thread
    partner_template = env.get_template("project_partnering_template.xml.jinja")
    partner_content = to_edstem(partner_template, **assignment_config)

    partner_thread = ed.post_thread(
        course_id,
        {
            "type": "post",
            "title": f"{bracketed_name} Search for a partner!",
            "category": "Project",
            "subcategory": f"{project_name}",
            "subsubcategory": f"{project_name} Logistics",
            "content": partner_content,
            "is_pinned": True,
            "is_private": post_privately,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True,
        }
    )
    partner_thread_num = partner_thread["number"]

    # task subthreads
    task_template = env.get_template("project_subthread_template.xml.jinja")
    task_threads: List[Dict[str, Any]] = []

    # needs to be reversed because ed posts backwards for some reason
    for idx, task_name in enumerate(reversed(assignment_config["subthreads"]), start=1):
        # determine A/B label
        if "ab_cutoff" in assignment_config:
            thread_label = f"[{project_name}A]" if idx <= assignment_config["ab_cutoff"] else f"[{project_name}B]"
        else:
            thread_label = bracketed_name

        task_content = to_edstem(task_template, **assignment_config, sub_name=task_name)

        task_thread = ed.post_thread(
            course_id,
            {
                "type": "post",
                "title": f"{thread_label} Task {idx}: {task_name}",
                "category": "Project",
                "subcategory": f"{project_name}",
                "subsubcategory": f"{project_name} Logistics",
                "content": task_content,
                "is_pinned": False,
                "is_private": post_privately,
                "is_anonymous": False,
                "is_megathread": True,
                "anonymous_comments": True,
            }
        )
        task_threads.append(task_thread)

    # task summary string for megathread
    task_threads_sub = "".join(
        f"Task {i+1}: #{t['number']}<break />"
        for i, t in enumerate(task_threads)
    )

    # main megathread
    megathread_template = env.get_template("project_megathread_template.xml.jinja")
    megathread_content = to_edstem(
        megathread_template,
        **assignment_config,
        partner_thread_num=f"#{partner_thread_num}",
        project_subthreads=task_threads_sub
    )

    megathread_thread = ed.post_thread(
        course_id,
        {
            "type": "post",
            "title": f"{bracketed_name} Main Thread",
            "category": "Project",
            "subcategory": f"{project_name}",
            "subsubcategory": f"{project_name} Logistics",
            "content": megathread_content,
            "is_pinned": True,
            "is_private": post_privately,
            "is_anonymous": False,
            "is_megathread": True,
            "anonymous_comments": True,
        }
    )

    print(f"Partner Thread: #{partner_thread_num}")
    print(f"Task Threads: {[t['number'] for t in task_threads]}")
    print(f"Megathread: #{megathread_thread['number']}")

    return {
        "partner_thread": partner_thread,
        "task_threads": task_threads,
        "megathread": megathread_thread,
    }