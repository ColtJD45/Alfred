## v0.2.1 - Memory Agent and Weather Agent Optimization

## Memory Optimization
- Added a prefilter for longterm memory search to provide the model with refined information _to improve latency_

## Weather Optimization
- Changed the formatting for response of weather API in `get_forecast_weather` for faster model interpretation
- Changed `get_forecast_weather` function to accomodate for UTC offset to keep forecast from bleeding into the next day

## Optimized Alfred's prompt
- Added default location to Alfred's prompt to ensure he used `LOCATION` when no location specified

## DEBUG added
- Added `DEBUG` to `main.py` to assess workflow duration
- Added `DEBUG` to `chat_tools` to assess duration of `save_chat` and `load_chat_history`
- Added `DEBUG` to `memory_tools` to asses duration of:
  - `load_longterm_memory`
  - `save_longterm_memory`
  - `get_context`
- Added `DEBUG` to `weather_tools` to asses duration of:
  - `get_current_weather`
  - `get_forecast_weather`

## Chores
- Cleaned up `chat_tools` _removed past commented out functions_
