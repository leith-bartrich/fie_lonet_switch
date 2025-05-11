# FIE LO/NET SWiTCH (fie_lonet_switch)

## Goal

A local computer user oriented toolset for managing the local/network switch state for a user's tools and environment, in a user-friendly manner.

## Features

- **Tray Icon**: A tray icon that indicates the current state of the switch and allows the user to change it.

- **CLI**: A command line interface that allows the user to change the state of the switch and view its current state. e.g. "fie_lonet_switch lo" or "fie_lonet_switch net mycompany us".

- **Groups**: When switching the user can specify a name fo a group of things to switch.  When no group is specified it is assumed that all groups should be switched.  The group name is a string that can be anything the user wants.  It is not a directory or file name, but a logical grouping of things.

- **Locales**: When switching to a network mode, the user can specify a name of a locale to switch to.  When specifying no locale, it can assumed to mean no_locale, or global_locale, or whatever makes sense for whatever cares about locales. Some consumers of the switch may not care about locales at all, and in that case the locale is ignored.  Intended (but not limited) usee case might be using us-east.docs.mycompany.com versus eu.docs.mycompany.com versus global.docs.mycompany.com.

- **Configuration**: A configuration directory (usually ~/.fie_lonet_switch) that allows the user to do useful things with the switch.

  - **python_scripts**: A sub-directory of configuration that allows any number of switch_*.py scripts to be run (imported) when the switch is changed.  A function named `switch_change` will be called if it exists with the following signature:

    ```python
    def switch_change(switch_to:str, group:str = "*", locale:str = "") -> None:
        """
        Called when the switch is changed.
        :param switch_to: The new switch state. Either "local" or "network".
        :param group: An optional named of the group of things that should be switched. Defaults to "*", which means 'all groups'.
        :param locale: An optional name of the locale to switch to. Defaults to empty string "" which means 'all locales' or 'no specific locale'.
        """
        pass
    ```

  - **switch_state.sql**: A SQLite database that contains the current state of the switch.  This is the state of the switch and also the semaphore for the user's switch.  All tools are required to touch and release quickly.

- **user_daemon****: A user daemon that can run in the background and watches for switch state changes.  It maintains an in-memory copy of the switch state and can be polled more freely by 3rd party tools.  It will also provide callback mechanisms.

  - **user_daemon.port**: a file in the configuration directory that contains the port number of the currently running daemon.  This allows 3rd party tools to find the daemon and attempt connection.

  - **user_daemon.key**: a file in the configuration directory that contains the current key of the currently running daemon.  This allows the daemon to authenticate 3rd party tools as having been given permission to connect. NOTE: this presumes that the user's home directory is secure.

## Implementation

We'll use the following libraries to implement the toolset:

- click: For the command line interface.
- textual for more complex toolsets.
- pyside6 for the tray icon.
- sqlite3 for the database.