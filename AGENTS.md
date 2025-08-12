# Project Agents.md Guide for OpenAI Codex

This Agents.md file provides guidance for OpenAI Codex and other AI agents working with this codebase.

## Project Structure for OpenAI Codex Navigation

- `/pixaris`: Core library code
  - `/data_loaders`: dataset loaders
  - `/experiment_handlers`: experiment orchestration
  - `/feedback_handlers`: feedback handling
  - `/generation`: image generation modules
  - `/metrics`: evaluate experiment
  - `/frontend`: Gradio UI components
  - `/orchestration`: glue between the components
  - `/utils`: helper utilities
- `/examples`: Example scripts demonstrating usage
- `/test`: Pytest suite for maintaining quality
- `/docs`: Documentation built with Sphinx
- `/assets`: Static images and other assets; these should not be modified directly

## Coding Conventions for OpenAI Codex

### General Conventions for Agents.md Implementation

- Use Python with type hints for all new code
- Follow the existing code style
- Provide descriptive variable and function names
- Add docstrings for non-trivial logic
- Format code with `make fmt` and lint with `make lint`

### Gradio UI Components Guidelines for OpenAI Codex

- Use Gradio Blocks when adding UI functionality
- Keep components small and well typed
- Prefer a functional style with clear input and output annotations

### Styling Standards for OpenAI Codex

- Gradio theming is handled centrally; avoid custom CSS unless necessary

## Testing Requirements for OpenAI Codex

Run tests with:

```bash
make test
```

## Pull Request Guidelines for OpenAI Codex

1. Provide a clear description of the changes
2. Reference related issues if applicable
3. Ensure `make lint` and `make test` succeed
4. Include screenshots for UI changes
5. Keep each PR focused on a single topic

## Programmatic Checks for OpenAI Codex

Before submitting changes, run:

```bash
make lint
make test
```

All checks must pass or note any issues in the PR description.
