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
