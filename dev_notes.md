## v0.3.0 - Move to langgraph builder / Node additions

## Switched from create_react_agent to nodes defined in a graph
- `router_node` - now handles initial user prompt and decides the next node via local `llama3.2:8b`
- `memory_node` - used when the prompt requires context or user history/preferences. Fine tuning needed
- `task_node` - used when the prompt requires manipulation or creation of a task in the SQLite3 database
- `weather_node` - used when the prompt requires real time weather information
- `builder.py` - builds graph for the movement of `state` through the graph
- `state.py` - initializes `state`

## Created router node
- Router node uses local `llama3.2:8b` to output `"next": 'node'` 
- Great success for correct node decision in testing so far.
- Works faster than OpenAI API
- No tokens used with local `llama3.2:8b`
- OpenAI llm commented out in the node to switch back and forth for testing

## Created task node
- Defined `task_node` to handle task related queries
- Created initial prompt for `task_node` to handle tools:
  - `create_new_task`
  - `get_tasks`
  - `mark_task_completed`
- Gave `create_new_task` the ability to add times to the the task `due_date`
- Task node is using `gpt-4o-mini` due to issues creating tool inputs with `llama3.2:8b`

## Created memory node
- Uses local `llama3.2:8b` for latency and privacy
- Added in this version to help with retrieving tasks for the user
- Some success with `save_longterm_memory` and `get_context` _this will be fine tuned with memory specific version update_

## Updated weather node
- Now uses local `llama3.2:8b` for latency and cost.
- Given access to tools for weather API to reduce prompt and latency

## Moved chat history
- removed `load_chat_history` from main.py
- `alfred_node` now loads the chat history for context to respond to the user

## Added date parser in location_date_tools
- Added `parse_date` to turn plain text day into assignable date and time for tasks

## Debugging additions
- Added in depth debugging in AI workflow

## Chores
- Cleaned up `chat_tools` _removed past commented out functions_
- Temporarily commented out `check_for_longterm_storage` in `main.py` _this will be addressed with `memory_node`_
- Removed personalization message from `main.py`
