import click
from fie_lonet_switch.switcher import do_switch
from fie_lonet_switch.database import SwitchStateDB, get_switch_state_transaction, compact_db_transaction, clear_group_transaction

@click.group()
def main():
    """FIE LO/NET Switch CLI."""
    pass

@main.command()
@click.argument('switch_to', type=click.Choice(['lo', 'net']))
@click.argument('group', required=False, default='*')
@click.argument('locale', required=False, default='')
def switch(switch_to, group, locale):
    """Switch the state to 'lo' or 'net'. Optionally specify group and locale."""
    do_switch(switch_to, group, locale)
    click.echo(f"Switched to {switch_to} (group: {group}, locale: {locale})")

@main.command()
@click.argument('group', required=False, default='*')
def status(group):
    """Show the current switch state for a group (default: all)."""
    db = SwitchStateDB()
    state, locale = get_switch_state_transaction(db, group)
    db.close()
    click.echo(f"Current state for group '{group}': {state} (locale: {locale})")

@main.command()
def compact():
    """Compact the switch state database to save space (keeps only the latest state per group)."""
    db = SwitchStateDB()
    try:
        compact_db_transaction(db)
        click.echo("Database compacted: only the latest state per group is kept.")
    except Exception as e:
        click.echo(f"Error compacting database: {e}")
    finally:
        db.close()

@main.command()
def list_all():
    """List all groups and their current switch states."""
    db = SwitchStateDB()
    try:
        groups = db.get_all_groups()
        if not groups:
            click.echo("No groups found in the database.")
            return
        for group in groups:
            state, locale = get_switch_state_transaction(db, group)
            click.echo(f"Group: {group} | State: {state} | Locale: {locale}")
    except Exception as e:
        click.echo(f"Error listing groups: {e}")
    finally:
        db.close()

@main.command()
@click.argument('group')
def clear_group(group):
    """Delete all switch state changes for a given group."""
    db = SwitchStateDB()
    try:
        clear_group_transaction(db, group)
        click.echo(f"All switch state changes for group '{group}' have been deleted.")
    except Exception as e:
        click.echo(f"Error clearing group '{group}': {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()