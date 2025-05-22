import click
from fie_lonet_switch.switcher import do_switch
from fie_lonet_switch.database import (
    SwitchStateDB,
    get_switch_state_transaction,
    compact_db_transaction,
    clear_group_transaction,
    JinjaTemplate,
)

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

@main.group()
def jinjas():
    """Manage jinja template paths."""
    pass


@jinjas.command("list")
def list_jinjas():
    """List the stored jinja template paths."""
    db = SwitchStateDB()
    try:
        templates = db.get_all_jinja_templates()
        for tmpl in templates:
            click.echo(tmpl.path)
    finally:
        db.close()


@jinjas.command("add")
@click.argument("path")
def add_jinja(path):
    """Add a jinja template path."""
    db = SwitchStateDB()
    try:
        db.begin()
        try:
            # Check for existing path; ignore if present
            db.get_jinja_template_by_path(path)
            db.rollback()
        except LookupError:
            tmpl = JinjaTemplate(path=path)
            db.create_jinja_template(tmpl)
            db.commit()
        click.echo(f"Added {path}")
    except Exception as e:
        db.rollback()
        click.echo(f"Error adding template '{path}': {e}")
    finally:
        db.close()


@jinjas.command("delete")
@click.argument("path")
def delete_jinja(path):
    """Remove a jinja template path."""
    db = SwitchStateDB()
    try:
        db.begin()
        try:
            db.delete_jinja_template_by_path(path)
        except LookupError:
            pass
        db.commit()
        click.echo(f"Deleted {path}")
    except Exception as e:
        db.rollback()
        click.echo(f"Error deleting template '{path}': {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()