## v0.3.1 - Memory Fine Tuning Update

## Fine tuning memory functions
- Added memory context to longterm memory decision tool to prevent duplicates and enrich memories
- `Memory node` uses `llama3.2` to search user's memories via `get_context`, then uses `gpt-3.5-turbo` to interpret them
- Changed memory related functions to `async`

## Router node adjustments
- Gave `router node` access to chat history
- Switched `router node` to gpt-3.5-turbo for better reasoning when user refers to previous chat messages for context
  - Example -
    _User: What tasks do I have today?_
    _Assistant: Your tasks for today are..._
    _User: What about tomorrow?_

    Previously using `llama3.2` without context, the router node would only see #What about tomorrow# and it would route this to the `weather node`. Now with `chat history` and `gpt-3.5-turbo` it can reason with previous messages and understand this needs to be sent to the task mode. 
    _A small amount of testing has shown success, but I assume there will be hiccups with the `task node` recieving only the last `user message` and no context. I will address that on a future version.

## Implemented `Zapier` for google calendar creation when creating new tasks
- Zapier API with defined dictionary for information about tasks created

## Chores
- Changed `[DEBUG]` prints for continuity
- Added `DEEP_DEBUG` for larger context debugging for things like forecast returns, internal llm prompt outputs, etc.
- Added `DEBUG` and `DEEP_DEBUG` to `backend/config.py` for centralized adjustments of debugging prints
- Added `DEBUG` and `DEEP_DEBUG` to .env file to adjust `true` or `false`

## Future upgrades
- Include Gmail monitoring to automatically create tasks via Zapier when email sent to home email address for things like:
  - Furnace filter change alerts
  - `Fixd` alerts for auto maintenance
  - Home insurance yearly reviews
  - Hot tub maintenance via monitoring app
  - Cold plunge maintenance via monitoring app
  - Smoke detector battery changes via home maintenance app
  - Home server maintenance and error faults via iDRAC email alerts
  - Automatically create a task to call and schedule dog grooming/healthcare via reminder emails
  - Create template for setting up any creation of a task based on received emails

## Future Future upgrades
- Implement `OpenAI API` with curated promting to analyze these emails and create these tasks based on:
  - Schedule availability
  - Urgency of specific task
  - Combination of like tasks for efficiency
  - Ability to change an already created tasks for room for a more important/urgent task