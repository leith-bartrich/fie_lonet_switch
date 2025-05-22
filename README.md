# FIE LoNet Switch

FIE LoNet Switch is a command-line tool for managing and switching between different configurations or environments. It is designed to be simple, fast, and easy to use.  It's user oriented and
for use by a user operator of a computer system.  Often a mobile workstation or laptop.

## Features
- Switch between different environments or configurations
- Manage environment settings from the command line
- Lightweight and easy to install

## Installation

1. Clone the repository:

```sh
git clone https://github.com/leith-bartrich/fie_lonet_switch.git
cd fie_lonet_switch
```

2. Install the package globally (recommended for CLI usage):

```sh
pip install .
```

## CLI Usage

After installation, you can use the CLI tool as follows:

```sh
fie_lonet_switch [OPTIONS] [COMMAND]
```

Replace `[OPTIONS]` and `[COMMAND]` with the appropriate options and commands for your use case. For detailed help, run:

```sh
fie_lonet_switch --help
```

The optional `GROUP` argument used by several commands accepts `*` to target all
groups. You may also use the alias `all` in place of `*`. Because `all` is
interpreted as this alias, it is reserved and cannot be used as a custom group
name.

### Example Usages

- Switch to local state for all groups:

  ```sh
  fie_lonet_switch switch lo
  ```

- Switch to network state for a specific group:

  ```sh
  fie_lonet_switch switch net mygroup
  ```

- Switch to local state for a group and locale:

  ```sh
  fie_lonet_switch switch lo mygroup us-east
  ```

- Show the current switch state for *all* group:

  ```sh
  fie_lonet_switch status
  ```

- Show the current switch state for a specific group:

  ```sh
  fie_lonet_switch status mygroup
  ```

- List all groups and their current switch states:

  ```sh
  fie_lonet_switch list_all
  ```

- Compact the switch state database (rarely needed but can improve performance):

  ```sh
  fie_lonet_switch compact
  ```

- Clear all switch state for a group:

  ```sh
  fie_lonet_switch clear_group mygroup
  ```

- List all configured Jinja template paths:

  ```sh
  fie_lonet_switch jinjas list
  ```

- Add a Jinja template path:

  ```sh
  fie_lonet_switch jinjas add /path/to/template.jinja
  ```

  Add a template path for a specific group:

  ```sh
  fie_lonet_switch jinjas add /path/to/other_template.jinja mygroup
  ```

- Delete a Jinja template path:

  ```sh
  fie_lonet_switch jinjas delete /path/to/template.jinja
  ```

## Switch Scripts

You can create switch scripts to automatic switcing of things based when you switch state.

Putting a file that matched "switch_*.py" in your ~/.fie_lonet_switch directory will cause it to be run when you switch state is how you do this.

The script will be imported as a module and the function "switch_change" will be called with the signature:

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

In this manner you can generally do whatever you want when the switch state changes.

## Jinja Templates

Jinja templates can be registered with the CLI so they are rendered every time
the switch state changes.  Add a path to a `.jinja` file using:

```sh
fie_lonet_switch jinjas add /path/to/config.conf.jinja [group]
```

When a switch occurs the template is rendered to a file of the same name without
the `.jinja` extension.  Each template receives a variable named
`fie_lonet_switch` providing information about the current switch:

```json
{
  "switch": {
    "switch_to": "lo" | "net",
    "group": "group name",
    "locale": "locale name"
  }
}
```

### Switching sections based on lo/net

```jinja
{% if fie_lonet_switch.switch.switch_to == "lo" %}
# using local resources
USE_LOCAL_SERVICES=true
{% else %}
# using network resources
USE_LOCAL_SERVICES=false
{% endif %}
```

### Locale specific settings with fallback

```jinja
{% if fie_lonet_switch.switch.locale == "home" %}
SERVER_IP=192.168.1.10  # LAN
{% elif fie_lonet_switch.switch.locale == "global" %}
SERVER_IP=203.0.113.10  # Public
{% else %}
SERVER_IP=203.0.113.10  # fallback when locale unspecified
{% endif %}
```


## Current Status

The database and CLI work well enough to be useful.  The GUI is a work in progress.  The MacOS implementation is simple and seems functional.  But deployment via py2app is not really tested.  It might work?  If it does, it'll put a app bundle in the build subdirectory.  Which you can then drag to your applications folder.

```sh
python setup.py py2app
```

A windows and linux tray app should be simple to implement but I've not gotten around to it.

The design makes mention of a user daemon.  It's not implemented yet.  But it will eventually be because it's something I'd eventually use.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. All contributions are welcome!