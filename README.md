# FIE Lonet Switch

FIE Lonet Switch is a command-line tool for managing and switching between different configurations or environments. It is designed to be simple, fast, and easy to use.

## Features
- Switch between different environments or configurations
- Manage environment settings from the command line
- Lightweight and easy to install

## Installation

1. Clone the repository:
   ```sh
git clone <repository-url>
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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
