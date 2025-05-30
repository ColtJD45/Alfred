## v0.2.0 - Memory Agent Implementation (WIP)

- Refactored Alfred to support version-based directory structure
- Added new `memory_agent` in `memory_node`
- Updated supervisor workflow to include `memory_agent`

## Memory Agent Added
- Added new `memory_agent` in `memory_node` for use by `supervisor`

- Created memory function for use by memory_agent:
  - `get_context`: used when memory_agent decides it needs historical context about the user
    This function uses the local `llama3:8b` model to search all of the historical context of the specified user, and returns
    the relevant information to the `memory_agent`

## Long term memory decision added for each prompt
- Each prompt is now sent to `llama3` for it to decide if the information needs to be stored in the user's longterm memory database
  _This decision making process model will most likely undergo further training for accuracy in future versions_

## Reorganized tools into corresponding files for use cases. Removed tools from node scripts.

- Migrated the following functions from `tools` to `memory_tools`:
  - `check_for_longterm_storage`
  - `save_longterm_memory`
  - `get_context`
  - `load_longterm_memory`

- Migrated the following functions from `tools` to `chat_tools`:
  - `create_chat_entry`
  - `load_chat_history`
  - `save_chat_message`

- Migrated the following functions from `tools` to `task_tools`: _The task agent will be implemented in a future version_
  - `create_task`
  - `get_tasks`
  - `mark_task_completed`

- Migrated the following functions from `tools` to `location_date_tools`:
  - `get_current_date`
  - `get_lat_lon`

- Migrated the following functions from `weather_node` to `weather_tools`:
  - `get_current_weather`
  - `get_forecast_weather`

## Adjustments made for changes throughout

- Updated all imports in `main.py`, `alfred_nodepy`, `weather_node.py` to accomodate tool relocations.

- Removed utils/tools.py
- Removed nodes/memory_llama.py

# Chores
- Updated file path comments at the top of each script to match `alfred` name change.