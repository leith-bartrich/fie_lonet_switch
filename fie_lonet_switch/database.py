import os
import sqlite3
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple, Literal
import uuid
from datetime import datetime

class SwitchStateChange(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the state change event.")
    c_time: datetime = Field(default_factory=datetime.utcnow, description="Creation time (UTC) of the state change event.")
    mode: Literal["lo", "net"] = Field(..., description="Switch mode: 'lo' for local, 'net' for network.")
    group: str = Field(default="*", description="Group name for the switch event.")
    locale: str = Field(default="", description="Locale for the switch event.")

class JinjaTemplate(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the template.")
    path: str = Field(..., description="Path to .jinja template file")
    group: str = Field(default="*", description="Group associated with this template.")

    @validator('path')
    def _validate_path(cls, v: str) -> str:
        if not v.endswith('.jinja'):
            raise ValueError('path must end with .jinja')
        return v

class SwitchStateDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            config_dir = Path.home() / ".fie_lonet_switch"
            config_dir.mkdir(parents=True, exist_ok=True)
            db_path = config_dir / "switch_state.sql"
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_schema()

    def _create_schema(self):
        cur = self.conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS switch_state_change (
                id TEXT PRIMARY KEY,
                c_time TEXT NOT NULL,
                mode TEXT NOT NULL,
                group_name TEXT NOT NULL,
                locale TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS jinja_templates (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                group_name TEXT NOT NULL DEFAULT '*'
            )
        ''')
        cur.execute("PRAGMA table_info(jinja_templates)")
        cols = [row[1] for row in cur.fetchall()]
        if 'group_name' not in cols:
            cur.execute('ALTER TABLE jinja_templates ADD COLUMN group_name TEXT NOT NULL DEFAULT "*"')
        self.conn.commit()

    def close(self):
        self.conn.close()

    # Transaction methods
    def begin(self):
        self.conn.execute('BEGIN')

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    # CRUD methods
    def create_switch_state_change(self, change: 'SwitchStateChange') -> None:
        cur = self.conn.cursor()
        try:
            cur.execute('''
                INSERT INTO switch_state_change (id, c_time, mode, group_name, locale)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(change.id),
                change.c_time.isoformat(),
                change.mode,
                change.group,
                change.locale
            ))
        except sqlite3.IntegrityError as e:
            raise ValueError(f"SwitchStateChange with id {change.id} already exists.") from e

    def get_switch_state_change(self, id: str) -> 'SwitchStateChange':
        cur = self.conn.cursor()
        cur.execute('SELECT id, c_time, mode, group_name, locale FROM switch_state_change WHERE id = ?', (id,))
        row = cur.fetchone()
        if row:
            return SwitchStateChange(
                id=row[0],
                c_time=row[1],
                mode=row[2],
                group=row[3],
                locale=row[4]
            )
        raise LookupError(f"SwitchStateChange with id {id} not found.")

    def get_all_switch_state_changes(self) -> List['SwitchStateChange']:
        cur = self.conn.cursor()
        cur.execute('SELECT id, c_time, mode, group_name, locale FROM switch_state_change')
        rows = cur.fetchall()
        return [
            SwitchStateChange(
                id=row[0],
                c_time=row[1],
                mode=row[2],
                group=row[3],
                locale=row[4]
            ) for row in rows
        ]

    def update_switch_state_change(self, change: 'SwitchStateChange') -> None:
        cur = self.conn.cursor()
        cur.execute('''
            UPDATE switch_state_change
            SET c_time = ?, mode = ?, group_name = ?, locale = ?
            WHERE id = ?
        ''', (
            change.c_time.isoformat(),
            change.mode,
            change.group,
            change.locale,
            str(change.id)
        ))
        if cur.rowcount == 0:
            raise LookupError(f"SwitchStateChange with id {change.id} not found for update.")

    def delete_switch_state_change(self, id: str) -> None:
        cur = self.conn.cursor()
        cur.execute('DELETE FROM switch_state_change WHERE id = ?', (id,))
        if cur.rowcount == 0:
            raise LookupError(f"SwitchStateChange with id {id} not found for deletion.")
        
    def delete_switch_state_changes_for_group(self, group: str) -> None:
        """
        Delete all switch state changes for a given group.
        Args:
            group (str): The group name for which to delete all switch state changes.
        """
        cur = self.conn.cursor()
        cur.execute('DELETE FROM switch_state_change WHERE group_name = ?', (group,))
        # No error if nothing deleted; silent if group not found

    def get_latest_switch_state_change_for_group(self, group: str) -> 'SwitchStateChange':
        cur = self.conn.cursor()
        cur.execute('''
            SELECT id, c_time, mode, group_name, locale FROM switch_state_change
            WHERE group_name = ?
            ORDER BY c_time DESC
            LIMIT 1
        ''', (group,))
        row = cur.fetchone()
        if row:
            return SwitchStateChange(
                id=row[0],
                c_time=row[1],
                mode=row[2],
                group=row[3],
                locale=row[4]
            )
        raise LookupError(f"No switch state change found for group '{group}'.")

    def get_all_groups(self) -> List[str]:
        cur = self.conn.cursor()
        cur.execute('SELECT DISTINCT group_name FROM switch_state_change')
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def clear_switch_state_changes(self) -> None:
        cur = self.conn.cursor()
        cur.execute('DELETE FROM switch_state_change')

    # Jinja template CRUD methods
    def create_jinja_template(self, template: 'JinjaTemplate') -> None:
        cur = self.conn.cursor()
        try:
            cur.execute('''
                INSERT INTO jinja_templates (id, path, group_name)
                VALUES (?, ?, ?)
            ''', (
                str(template.id),
                template.path,
                template.group
            ))
        except sqlite3.IntegrityError as e:
            raise ValueError(f"JinjaTemplate with id {template.id} or path {template.path} already exists.") from e

    def get_jinja_template(self, id: str) -> 'JinjaTemplate':
        cur = self.conn.cursor()
        cur.execute('SELECT id, path, group_name FROM jinja_templates WHERE id = ?', (id,))
        row = cur.fetchone()
        if row:
            return JinjaTemplate(id=row[0], path=row[1], group=row[2])
        raise LookupError(f"JinjaTemplate with id {id} not found.")

    def get_all_jinja_templates(self) -> List['JinjaTemplate']:
        cur = self.conn.cursor()
        cur.execute('SELECT id, path, group_name FROM jinja_templates')
        rows = cur.fetchall()
        return [JinjaTemplate(id=row[0], path=row[1], group=row[2]) for row in rows]

    def update_jinja_template(self, template: 'JinjaTemplate') -> None:
        cur = self.conn.cursor()
        try:
            cur.execute('''
                UPDATE jinja_templates
                SET path = ?,
                    group_name = ?
                WHERE id = ?
            ''', (
                template.path,
                template.group,
                str(template.id)
            ))
        except sqlite3.IntegrityError as e:
            raise ValueError(
                f"JinjaTemplate with path {template.path} already exists."
            ) from e
        if cur.rowcount == 0:
            raise LookupError(
                f"JinjaTemplate with id {template.id} not found for update."
            )

    def delete_jinja_template(self, id: str) -> None:
        cur = self.conn.cursor()
        cur.execute('DELETE FROM jinja_templates WHERE id = ?', (id,))
        if cur.rowcount == 0:
            raise LookupError(f"JinjaTemplate with id {id} not found for deletion.")

    def get_jinja_template_by_path(self, path: str) -> 'JinjaTemplate':
        cur = self.conn.cursor()
        cur.execute('SELECT id, path, group_name FROM jinja_templates WHERE path = ?', (path,))
        row = cur.fetchone()
        if row:
            return JinjaTemplate(id=row[0], path=row[1], group=row[2])
        raise LookupError(f"JinjaTemplate with path {path} not found.")

    def delete_jinja_template_by_path(self, path: str) -> None:
        cur = self.conn.cursor()
        cur.execute('DELETE FROM jinja_templates WHERE path = ?', (path,))
        if cur.rowcount == 0:
            raise LookupError(f"JinjaTemplate with path {path} not found for deletion.")

def switch_change_transaction(db: SwitchStateDB, switch_to:Literal['lo', 'net'], group:str = "*", locale:str = "") -> None:
    """
    Perform a switch change transaction.
    
    Args:
        db (SwitchStateDB): The database connection.
        switch_to (Literal['lo', 'net']): The mode to switch to ('lo' for local, 'net' for network).
        group (str): The group name for the switch event.
        locale (str): The locale for the switch event.
    """
    change = SwitchStateChange(mode=switch_to, group=group, locale=locale)
    db.begin()

    if group == "*":
        # a * change overrides all things.
        db.clear_switch_state_changes()

    change = SwitchStateChange(
        id=uuid.uuid4(),
        c_time=datetime.now(),
        mode=switch_to,
        group=group,
        locale=locale
    )
    try:
        db.create_switch_state_change(change)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    
def get_switch_state_transaction(db: SwitchStateDB, group:str="*") -> Tuple[str,str]:
    """
    Get's the current switch state for the given group.  If no grop is provided it will use the default/all group "*"
    Also returns the locale for a net switch, which will often by an empty string.
    Args:
        db (SwitchStateDB): The database connection.
        group (str): The group name for the switch event.
    Returns:
        Tuple[switch_state:str,locale:str]: The current switchstate is ('lo' or 'net') and the locale for a net switch.
    """
    # Get the latest switch state change for the specified group or set None
    try:
        group_specific_change = db.get_latest_switch_state_change_for_group(group)
    except LookupError:
        group_specific_change = None
    # Get the latest switch state change for all groups or set None
    try:
        all_change = db.get_latest_switch_state_change_for_group("*")
    except LookupError:
        all_change = None

    if group_specific_change is None:
        if all_change is None:
            # If both are None, we return the default state
            return "lo", ""
        else:
            # If only the all change is found, return that
            return all_change.mode, all_change.locale
    else:
        # If both changes are found, compare their creation times if not, we return the group-specific change
        if all_change is None:
            # If only the group-specific change is found, return that
            return group_specific_change.mode, group_specific_change.locale
        else:
            # Compare the creation times and return the most recent one
            if group_specific_change.c_time > all_change.c_time:
                return group_specific_change.mode, group_specific_change.locale
            else:
                return all_change.mode, all_change.locale

def compact_db_transaction(db: SwitchStateDB) -> None:
    """
    Compact the database to save space.
    
    Args:
        db (SwitchStateDB): The database connection.
    """
    db.begin()
    to_keep:List[SwitchStateChange] = []
    try:
        for group in db.get_all_groups():
            to_keep.append(db.get_latest_switch_state_change_for_group(group))
        db.clear_switch_state_changes()
        for change in to_keep:
            db.create_switch_state_change(change)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

def clear_group_transaction(db: SwitchStateDB, group: str) -> None:
    """
    Delete all switch state changes for a given group in a transaction.
    Args:
        db (SwitchStateDB): The database connection.
        group (str): The group name to clear.
    """
    db.begin()
    try:
        db.delete_switch_state_changes_for_group(group)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e