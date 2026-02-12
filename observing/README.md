# Gap Observation Note Action

Generate a structured, gap-driven observation note in Chinese using Gemini.

## Inputs

- `observation` (required): Raw observation text to rewrite into a structured note.
- `scenario` (optional): Additional context about the scenario.
- `perspective` (optional): Observer perspective.
- `output_dir` (optional, default: `output/observing`): Where to write the generated note.
- `gemini_api_key` (optional): Gemini API key. If omitted, `GEMINI_API_KEY` or `GEMINI` env will be used.
- `gemini_model` (optional, default: `gemini-2.5-flash`): Gemini model name.

## Outputs

- `note_path`: Full path to the generated note file.
- `note_dir`: Output directory path.
- `note_filename`: Filename of the generated note.

## Example Workflow

```yaml
name: Observing Note

on:
  workflow_dispatch:
    inputs:
      observation:
        description: Observation text
        required: true
      scenario:
        description: Scenario context
        required: false
      perspective:
        description: Observer perspective
        required: false

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate note
        uses: ./observing
        with:
          observation: ${{ inputs.observation }}
          scenario: ${{ inputs.scenario }}
          perspective: ${{ inputs.perspective }}
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Local Run

```bash
node observing/generate_observation.mjs \
  --observation "..." \
  --scenario "..." \
  --perspective "..." \
  --gemini-api-key "$GEMINI_API_KEY"
```
