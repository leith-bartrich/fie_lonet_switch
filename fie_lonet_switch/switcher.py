from fie_lonet_switch.database import switch_change_transaction, SwitchStateDB
from pathlib import Path
from typing import Literal

def do_switch(switch_to:Literal["lo","net"], group:str = "*", locale:str = "") -> None:
    """
    Switch the state of the switch to either 'lo' or 'net'.
    
    Args:
        switch_to (str): The state to switch to ('lo' or 'net').
        group (str): The group name to filter by.
        locale (str): The locale to filter by.
    """
    print(f"Switching to {switch_to} for group {group} with locale {locale}.")
    db = SwitchStateDB()
    switch_change_transaction(db, switch_to, group, locale)
    db.close()
    print(f"database updated.")
    do_switch_jinjas_in_db(switch_to, group, locale)
    do_homedir_switch_scripts(switch_to, group, locale)


def do_homedir_switch_scripts(switch_to: Literal["lo", "net"], group: str = "*", locale: str = "") -> None:
    """Run any homedir switch scripts that exist."""
    for script in Path.home().glob(".fie_lonet_switch/switch_*.py"):
        print(f"Importing script {script}")
        import importlib.util
        spec = importlib.util.spec_from_file_location("switch_script", script)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "switch_change"):
                    func = getattr(module, "switch_change")
                    if callable(func):
                        print(f"Calling switch_change in {script}")
                        func(switch_to, group, locale)
                    else:
                        print(f"switch_change in {script} is not callable.")
                else:
                    print(f"No switch_change function in {script}.")
            except Exception as e:
                print(f"Error importing or running {script}: {e}")
        else:
            print(f"Could not load spec for {script}.")


def do_switch_jinjas_in_db(
    switch_to: Literal["lo", "net"], group: str = "*", locale: str = ""
) -> None:
    """Render jinja templates stored in the database."""
    db = SwitchStateDB()
    templates = db.get_all_jinja_templates()
    db.close()

    for tmpl in templates:
        if group != "*" and tmpl.group.lower() != group.lower():
            continue

        jinja_path = Path(tmpl.path)
        if not jinja_path.exists():
            print(f"WARNING: Template {jinja_path} does not exist")
            continue

        try:
            from jinja2 import Template

            text = jinja_path.read_text()
            template = Template(text)
            rendered = template.render(
                {
                    "fie_lonet_switch": {
                        "switch": {
                            "switch_to": switch_to,
                            "group": group,
                            "locale": locale,
                        }
                    }
                }
            )
            output_path = jinja_path.with_suffix("")
            output_path.write_text(rendered)
            print(f"Rendered {jinja_path} -> {output_path}")
        except Exception as e:
            print(f"Error processing {jinja_path}: {e}")
