```json
{
  "owner": "mihail911",
  "name": "modern-software-dev-assignments",
  "full_name": "mihail911/modern-software-dev-assignments",
  "url": "https://github.com/mihail911/modern-software-dev-assignments",
  "description": "Assignments for CS146S: The Modern Software Dev (Stanford University Fall 2026/2025)",
  "readme_sha256": "572a569634919471bb37741a5c3fa6bfb7c412a908b34448b2c51f567bac6666"
}
```

# mihail911/modern-software-dev-assignments

- URL: https://github.com/mihail911/modern-software-dev-assignments
- Description: Assignments for CS146S: The Modern Software Dev (Stanford University Fall 2026/2025)
- README SHA256: `572a569634919471bb37741a5c3fa6bfb7c412a908b34448b2c51f567bac6666`

## README

# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Repo Setup
These steps work with Python 3.12.

1. Install Anaconda
   - Download and install: [Anaconda Individual Edition](https://www.anaconda.com/download)
   - Open a new terminal so `conda` is on your `PATH`.

2. Create and activate a Conda environment (Python 3.12)
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. Install Poetry
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. Install project dependencies with Poetry (inside the activated Conda env)
   From the repository root:
   ```bash
   poetry install --no-interaction
   ```
