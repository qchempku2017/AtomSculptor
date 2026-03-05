# AtomSculptor

Materials-science agent workspace using Google ADK + Anthropic Sandbox Runtime (`srt`).

## Requirements

- Linux (current project environment)
- Python 3.10+
- Node.js + npm
- `srt` Linux dependencies:
  - `bubblewrap`
  - `socat`
  - `ripgrep`

Ubuntu/Debian example:

```bash
sudo apt-get update
sudo apt-get install -y bubblewrap socat ripgrep
```

---

## 1) Create Python environment

```bash
cd /home/notfish/dev/AtomSculptor
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install google-adk pyyaml
```

If you use a different model backend, also install any provider SDK required by your LiteLLM model setup.

---

## 2) Install sandbox runtime CLI (`srt`)

```bash
npm install -g @anthropic-ai/sandbox-runtime
srt --help
```

---

## 3) Configure project

Edit `config.yaml`:

```yaml
PLANNER_MODEL: "openai/qwen3-max"
SANDBOX_DIR: "sandbox/runtime"
```

You can also override with env vars:

```bash
export PLANNER_MODEL="openai/qwen3-max"
export SANDBOX_DIR="sandbox/runtime"
```

Set your provider credentials as needed (example):

```bash
export OPENAI_API_KEY="<your_key>"
```

---

## 4) Run the agent

From repo root:

```bash
adk run agent_team
```

If this command fails, verify:

1. Virtual env is active.
2. `google-adk` is installed in that env.
3. Model/API credentials are set.
4. `srt` is installed and Linux deps are present.

---

## Sandbox usage in code

The project exposes a Python wrapper around `srt` in `sandbox/core.py`.

Basic pattern:

```python
from sandbox import Sandbox

sandbox = Sandbox("sandbox/runtime")
sandbox.add_agent(agent)              # or sandbox.add_agent([agent1, agent2])
result = sandbox.run("echo hello")
print(result.stdout)
```

What it does:

- Creates sandbox workspace folder at `sandbox/runtime`
- Stores internal sandbox control files under `sandbox/.sandbox_control/`
  - `sandbox/.sandbox_control/srt-settings.json`
  - `sandbox/.sandbox_control/agents/<agent_name>/`
- Runs commands through:
  - `srt --settings <sandbox_settings_path> <command>`

---

## Useful files

- `agent_team/agent.py` — root ADK agent wiring
- `agent_team/agents/planner.py` — planner definition + tools
- `sandbox/core.py` — `Sandbox` class
- `sandbox/tools.py` — file tools used by planner
- `settings.py` — loads config/env settings
- `config.yaml` — default runtime config

---

## Quick sanity checks

```bash
python -c "from sandbox import Sandbox; s=Sandbox('sandbox/runtime'); print(s.list_agents())"
srt --version
```
