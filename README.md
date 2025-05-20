# az-rag-experiments

This is a Python project using [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

## Getting Started

### Content Understanding RAG

Using [Azure AI Content Understanding](https://learn.microsoft.com/en-us/azure/cognitive-services/content-understanding/overview) and [Azure AI Search](https://learn.microsoft.com/en-us/azure/search/) to create a Retrieval-Augmented Generation (RAG) pipeline.

> Code and inspiration from https://github.com/Azure-Samples/azure-ai-search-with-content-understanding-python/blob/main/notebooks/search_with_multimodal_RAG.ipynb

1. **Set up environment variables:**

   - Copy `.env.example` to `.env` in `src/az-content-understanding/` and fill in your values.
   - If you need sample data, copy `data.example/` to `data/` at the project root, or create your own `/data` folder and populate it with PDFs and images.

2. **Create and activate the virtual environment:**

   ```zsh
   cd src/az-content-understanding
   uv venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**

   ```zsh
   uv pip install .
   ```

   This will install all dependencies listed in `pyproject.toml`.

4. **Run the main script:**
   ```zsh
   python main.py
   ```
   Or use the VS Code task "Run az-content-understanding" for one-click execution.

## Project Structure

- `src/az-content-understanding/` - Main Python package and code
  - `main.py` - Entry point script
  - `pyproject.toml` - Project metadata and dependencies (used by uv)
  - `.env.example` - Example environment variable file (copy to `.env`)
- `data.example/` - Example data (copy to `data/` for use)
- `.github/copilot-instructions.md` - Copilot custom instructions
- `.gitignore` - Standard Python, VS Code, and environment ignores

## Notes

- Do **not** use `requirements.txt`; all dependencies are managed in `pyproject.toml`.
- Make sure you have [uv](https://github.com/astral-sh/uv) installed for best performance.
- For more info on uv, see the [uv documentation](https://github.com/astral-sh/uv).
