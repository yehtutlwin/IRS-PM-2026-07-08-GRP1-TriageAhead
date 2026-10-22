# Platform setup: Windows (WSL2) and macOS

The scripts assume a Unix shell (`bash`, `curl`, `python3` 3.10 or later). On Windows that means **WSL2**; the `.sh` scripts do not run from PowerShell or Git Bash. On macOS everything runs natively. After the platform part below, continue with the [installation and user guide](install-and-user-guide.md).

## Windows 10/11: WSL2

**1. Install WSL2 with Ubuntu** (skip if you already have it). In PowerShell *as administrator*:

```powershell
wsl --install -d Ubuntu
```

Reboot when prompted, open the "Ubuntu" app and create your Linux username. Everything below happens inside that Ubuntu terminal.

**2. Install the basics:**

```bash
sudo apt update && sudo apt install -y git curl python3-venv python3-pip
```

**3. Put the repository in the Linux filesystem**, under your Linux home (`~/...`), not under `/mnt/c/...`. The Windows-mounted paths are much slower and cause permission and line-ending problems. Either clone the submission repository there or unzip it there, then:

```bash
cd IRS-PM-2026-07-08-GRP1-TriageAhead/SystemCode
```

**4. Continue with the installation guide** (a virtual environment is strongly recommended over a global `pip`):

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash sources/download.sh
cp .env.example .env        # then choose a language-model backend, as the installation guide explains
```

**5. Editor and browser:**

- VS Code: install the **WSL extension** on the Windows side, then run `code .` inside the folder for a native editing experience against the Linux files.
- Anything the app serves on `localhost` is reachable from your normal Windows browser; WSL2 forwards localhost automatically.

**6. Optional: the local language model on a GPU (Ollama).** Works on a machine with an NVIDIA GPU of about 8 GB or more of memory:

- Install the normal **Windows** NVIDIA driver only; never install a driver inside WSL. `nvidia-smi` inside Ubuntu should show the GPU.
- Then inside Ubuntu:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:12b          # about 7 GB to download
echo "LLM_BACKEND=ollama" >> .env
```

If `ollama ps` shows something other than `100% GPU` after a chat turn, the model spilled to the CPU: close memory-hungry Windows applications, or use a cloud backend.

## macOS

**1. Check Python**, 3.10 or later:

```bash
python3 --version
```

If it is older or missing, install it with [Homebrew](https://brew.sh): `brew install python git`.

**2. Set up**, from the `SystemCode` folder of the submission repository:

```bash
cd IRS-PM-2026-07-08-GRP1-TriageAhead/SystemCode
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash sources/download.sh
cp .env.example .env        # then choose a language-model backend, as the installation guide explains
```

**3. Optional: the local language model (Ollama).**

- **Apple Silicon (M1 to M4):** install the Ollama app from [ollama.com/download](https://ollama.com/download) (or `brew install ollama`), then `ollama pull gemma4:12b` and set `LLM_BACKEND=ollama` in `.env`. The GPU (Metal) is used automatically. Rule of thumb: 16 GB or more of unified memory for the 12B model; on an 8 GB Mac use a cloud backend.
- **Intel Macs:** no usable GPU path; Ollama runs on the CPU only and slowly, so use a cloud backend.

## Both platforms: quick reference

```bash
source .venv/bin/activate                     # each new terminal
python3 prototype/run.py dry                  # the engine alone, no language model needed
bash webapp/run.sh                            # the intake app with a public address and QR code
python3 -m pytest tests/                      # the handbook's cases against the rules
```

The Yale explorer workbook (`data/yale-explorer.xlsx`) can be regenerated after `bash data/download-yale.sh` with `python3 data/make-yale-explorer.py`.
