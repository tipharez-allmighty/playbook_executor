# Playbook Executor

A lightweight, high-performance asynchronous SSH task runner. This tool allows execution of bash commands across multiple host groups simultaneously with builtin concurrency limiting and safety timeouts.

The executor is split into two main engines: the Parser and the Runner.

**1. The Parser (The Planner)**

Before a single connection is made, the parser safely maps out what needs to happen:

* **Reads & Validates:** It reads your YAML playbook and uses Pydantic to strictly validate the structure. If your YAML is malformed, it catches it immediately.
* **Maps Inventory:** It reads your hosts file, looking for `[groups]`. It matches these groups to the `hosts:` keys in your playbook.
* **Builds the Execution Plan:** It flattens this mapping into a concrete plan, attaching specific IP addresses to their required tasks while automatically skipping duplicate IPs to save time.

**2. The Runner (The Execution Engine)**

Once the plan is built, the runner takes over to execute it:

* **Asynchronous Execution:** It uses asyncio to bundle all tasks and fire them off simultaneously, rather than waiting for one server to finish before moving to the next.
* **Traffic Control:** It wraps the connections in an `asyncio.Semaphore`. If you have 100 tasks but a `MAX_CONCURRENT_TASKS` of 10, it ensures only 10 SSH connections are open at once, preventing your local machine from crashing or remote servers from rate-limiting you.
* **Live Log Streaming:** It uses asyncssh to execute the bash commands. It captures the output (stdout on success, stderr on failure) and streams it back to your console line-by-line with clean formatting, including the exact task name, IP, and success/fail status.

## Prerequisites

Before running the executor, the remote hosts (including localhost for testing) must have an SSH server active.

### SSH Service Setup

#### For Arch or Fedora Linux:

The service name is usually `sshd`.

```bash
# Start the SSH daemon
sudo systemctl start sshd
# Enable it to start on boot
sudo systemctl enable sshd
```

#### For Debian based systems (Ubuntu, Debian, Kali):

The service name is usually `ssh`.

```bash
# Start the SSH daemon
sudo systemctl start ssh
# Enable it to start on boot
sudo systemctl enable ssh
```

### Verification

To confirm your machine is ready to accept connections, run:

```bash
ssh localhost
```

> **Note:** If you get "Connection refused," the service is either not installed (`sudo apt install openssh-server`) or not started.

## Installation

### Install the Package Manager

#### Using `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment automatically
uv sync

# Activate the environment
source .venv/bin/activate
```

#### Or just use `pip`

```bash
python -m pip install --upgrade pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration (`.env`)

You can optionally create a `.env` file (or copy from an `.env.example`) to tune performance and security settings. If no `.env` file is provided, the executor will safely fall back to the following default values:

```bash
cp .env.example .env
```

You can then edit the `.env` file to change the following values:

-   `TASK_TIMEOUT`: tasks level timeout (seconds). *(Default: 10)*
-   `GLOBAL_TIMEOUT`: Maximum time for the entire playbook to run (seconds). *(Default: 600)*
-   `MAX_CONCURRENT_TASKS`: Number of simultaneous SSH connections. *(Default: 10)*
-   `SSH_KNOWN_HOSTS_FILE`: Path to your SSH known_hosts file (e.g., `~/.ssh/known_hosts`). *(Default: blank)* If provided, the executor enforces strict security and will instantly block connections to any server not listed in that file.

## Usage

### Testing

1.  **Run unit tests (Optional):**

    ```bash
    # Validate the internal logic, YAML parsing, and Pydantic schemas using pytest:
    uv run pytest
    ```

The `test_setup.sh` script handles: generating keys, authorizing SSH, and creating the `/etc/playbook` directory.

2.  **Run test setup script:**

    ```bash
    # Requires sudo for /etc/playbook creation
    bash test_setup.sh
    ```

3.  **Execute Playbook:**

    ```bash
    uv run python main.py playbooks/test.yaml
    ```

**What this script actually does:**

*   **Generates SSH Keys:** It checks for a local SSH key (`~/.ssh/id_rsa`). If you don't have one, it generates it automatically. If it already exists, you will see a message saying it's skipping generation.
*   **Authorizes Local Keys:** It takes your public key and adds it directly to your own `~/.ssh/authorized_keys` file. This allows your machine to SSH into itself without asking for a password.
*   **Deploys Test Inventory:** It prompts you asking if you want to create a default local hosts file. If you say yes, it will create `/etc/playbook/hosts` and fill it with dummy data (`localhost` and `127.0.0.1`). *Note: Unlike the prod script, if you answer yes here, it WILL overwrite any existing file at that location.*

### Production

To run against real servers:

1.  **Run setup script:**

    ```bash
    bash prod_setup.sh
    ```

2.  **Execute Playbook:**

    ```bash
    uv run python main.py playbooks/test.yaml
    ```

**What this script actually does:**

*   **Generates SSH Keys:** It looks for a local SSH key (`~/.ssh/id_rsa`). If you don't already have one, it generates it automatically in the background.
*   **Deploys the Inventory:** It checks if the system inventory (`/etc/playbook/hosts`) already exists. If it *doesn't*, it creates the directory and copies your local `hosts` file there. If it *does* exist, it leaves it alone and uses the existing file to protect your configuration.
*   **IMPORTANT! Authorizes servers:** It reads the IPs from the inventory file and runs `ssh-copy-id` against every server. This pushes your public key to the remote machines, allowing the Python script to connect without asking for passwords. If the key already exists on a remote server, it will show a warning and simply use the existing one without overwriting or failing.
