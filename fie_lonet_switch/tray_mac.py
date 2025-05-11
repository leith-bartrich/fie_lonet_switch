# Renamed to tray_mac.py. This file is now deprecated. Please use tray_mac.py for the macOS tray app implementation.

import rumps
from fie_lonet_switch.switcher import do_switch
from fie_lonet_switch.database import SwitchStateDB, get_switch_state_transaction, compact_db_transaction, clear_group_transaction

class FIELonetSwitchApp(rumps.App):
    def __init__(self):
        super().__init__("FIE Lonet Switch", icon=None, menu=[
            "Switch * to Local (lo)",
            "Switch * to Network (net)",
            "Switch Group to Local (lo)",
            "Switch Group to Network (net)",
            None,
            "List All Groups",
            None,
            "Compact Database",
            "Clear Group"
        ])
        self.title = "L/N"
        self.update_tooltip()

    def update_tooltip(self):
        self.tooltip = self.list_all_groups()

    def list_all_groups(self):
        db = SwitchStateDB()
        try:
            groups = db.get_all_groups()
            if not groups:
                return "No groups found."
            result = []
            for group in groups:
                state, locale = get_switch_state_transaction(db, group)
                result.append(f"Group: {group} | State: {state} | Locale: {locale}")
            return "\n".join(result)
        except Exception as e:
            return f"Error: {e}"
        finally:
            db.close()

    @rumps.clicked("Switch * to Local (lo)")
    def switch_all_lo(self, _):
        do_switch('lo', '*', '')
        self.update_tooltip()
        rumps.notification("FIE Lonet Switch", "Switched", "Switched all groups to local (no locale)")

    @rumps.clicked("Switch * to Network (net)")
    def switch_all_net(self, _):
        do_switch('net', '*', '')
        self.update_tooltip()
        rumps.notification("FIE Lonet Switch", "Switched", "Switched all groups to network (no locale)")

    @rumps.clicked("Switch Group to Local (lo)")
    def switch_lo(self, _):
        group = rumps.Window("Enter group name (or leave blank for all groups):", "Switch Group to Local (lo)").run().text
        locale = rumps.Window("Enter locale (or leave blank for all locales):", "Switch Group to Local (lo)").run().text
        if not group:
            group = "*"
        if not locale:
            locale = ""
        do_switch('lo', group, locale)
        self.update_tooltip()
        rumps.notification("FIE Lonet Switch", "Switched", f"Switched to local (group: {group}, locale: {locale})")

    @rumps.clicked("Switch Group to Network (net)")
    def switch_net(self, _):
        group = rumps.Window("Enter group name (or leave blank for all groups):", "Switch Group to Network (net)").run().text
        locale = rumps.Window("Enter locale (or leave blank for all locales):", "Switch Group to Network (net)").run().text
        if not group:
            group = "*"
        if not locale:
            locale = ""
        do_switch('net', group, locale)
        self.update_tooltip()
        rumps.notification("FIE Lonet Switch", "Switched", f"Switched to network (group: {group}, locale: {locale})")

    @rumps.clicked("List All Groups")
    def show_list_all(self, _):
        rumps.alert(self.list_all_groups())

    @rumps.clicked("Compact Database")
    def compact_db(self, _):
        db = SwitchStateDB()
        try:
            compact_db_transaction(db)
            rumps.notification("FIE Lonet Switch", "Database", "Database compacted.")
        except Exception as e:
            rumps.alert(f"Error: {e}")
        finally:
            db.close()
        self.update_tooltip()

    @rumps.clicked("Clear Group")
    def clear_group(self, _):
        group = rumps.Window("Enter group name to clear:", "Clear Group").run().text
        if group:
            db = SwitchStateDB()
            try:
                clear_group_transaction(db, group)
                rumps.notification("FIE Lonet Switch", "Clear Group", f"Cleared group '{group}'.")
            except Exception as e:
                rumps.alert(f"Error: {e}")
            finally:
                db.close()
            self.update_tooltip()

def main():
    FIELonetSwitchApp().run()

if __name__ == "__main__":
    main()
