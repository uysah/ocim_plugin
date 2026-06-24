#  📦 Object-Centric Inductive Miner Plugin 

This repository implements a Plugin for **Ocelescope** to discover Object-Centric Petri Nets and Object-Centric Process Trees with the Object-Centric Inductive Miner. The Plugin uses the implementation by Niklas van Detten, which can be found [here](https://github.com/Nik314/OCIM)




<!-- # Known Issues -->

<!-- - The ordering of children nodes are not yet considered, i.e., for **Sequence** and **Loop** Operators -->


<!-- An Ocelescope plugin is a **Python module packaged as a `.zip`** archive. The plugin module must expose **exactly one** plugin class (your `Plugin` subclass) from its `__init__.py` entry point. Your plugin methods are regular class methods decorated with `@plugin_method`. Their type hints define inputs and outputs in the UI.  
See the Ocelescope plugin docs for details.

## Requirements

- Python **3.13**
- A Python package manager (recommended: **uv**)

## Project layout

The actual plugin code lives in:

- `src/plugin-template/plugin.py` (plugin class, resources, inputs)
- `src/plugin-template/__init__.py` (exports your plugin class)

When you build the plugin, Ocelescope creates one or more `.zip` files in `dist/`.

## Quick start

1. Install dependencies.

   With **uv**:

   ```sh
   uv sync
   ```

   With **pip**:

   ```sh
   pip install -r requirements.txt
   ```

2. Open `src/plugin-template/plugin.py` and rename the plugin class and metadata.

   ```py
   class PluginTemplate(Plugin):
       label = "Minimal Plugin"
       description = "An Ocelescope plugin"
       version = "0.1.0"
   ```

3. Update the export in `src/plugin-template/__init__.py`.

   ```py
   from .plugin import PluginTemplate

   __all__ = [
       "PluginTemplate",
   ]
   ```

## Build

You can build the plugin `.zip` using the Ocelescope CLI:

```sh
ocelescope build
```

If you use **uv**:

```sh
uv run ocelescope build
```

The resulting `.zip` files are written to `dist/`.

## GitHub Actions release workflow

This repository includes a workflow that:

- builds the plugin ZIPs, and
- creates a GitHub Release with the ZIPs attached.

It runs when you push a tag that starts with `v`.

Example:

```sh
git tag v0.1.0
git push origin v0.1.0
```

## Notes and common pitfalls

- **Export exactly one plugin class.** Ocelescope expects a single plugin class exposed via `__init__.py`.
- **Use relative imports inside the plugin.** Avoid absolute imports within your plugin package.
- **Resources must be JSON-serializable.** Keep fields to standard JSON types (or Pydantic models). -->
