# SQL-CTF

SQL-CTF is a collection of intentionally vulnerable SQL-injection challenges created for **KSI**, a computer science seminar for high school students at Masaryk University.

The project contains:

- Four browser-based Flask challenges with different SQL-injection scenarios.
- A TCP blind-SQL challenge that can be accessed with the included client template.
- Docker Compose configuration for running the web and TCP services locally.

The vulnerabilities are deliberate and are intended for use in a controlled educational environment only.

## Prerequisites

Install the following software:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) with Docker Compose
- Python 3.11 or newer, if you want to run the blind-SQL client outside Docker

Node.js is not required.

## Setup and Installation

Clone the repository and enter its directory:

```bash
git clone https://github.com/DogoSlav/SQL-CTF.git
cd SQL-CTF
```

Create the local environment file from the provided template:

```bash
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Open `.env` and replace the placeholder values with the credentials, flags, token, and server settings for your seminar or local deployment. The `.env` file contains sensitive configuration and must not be committed to Git.

Build and start both services:

```bash
docker compose up --build
```

To start the services in the background:

```bash
docker compose up --build -d
```

## Usage

### Web challenges

The Flask web service is available at:

```text
http://localhost:8000
```

The individual challenges are mounted at:

| Challenge | URL |
|---|---|
| Challenge 1 | `http://localhost:8000/nuioghabyiaw/site1` |
| Challenge 2 | `http://localhost:8000/nuioghabyiaw/site2` |
| Challenge 3 | `http://localhost:8000/nuioghabyiaw/site3` |
| Challenge 4 | `http://localhost:8000/nuioghabyiaw/site4` |

Each challenge presents a different intentionally vulnerable application. Follow the challenge instructions and investigate the SQL behavior to reach its success page.

### Blind-SQL challenge

The blind-SQL service listens on TCP port `9999`:

```text
localhost:9999
```

The included client template can be run with Python after the environment variables have been configured:

```bash
python blind_sql_challenge/template.py
```

The client reads `CHALLENGE_TOKEN`, `BLIND_SQL_PORT`, and `BLIND_SQL_SERVER_HOST` from the environment. When connecting to the locally running Docker service, set `BLIND_SQL_SERVER_HOST=localhost` in your local environment before starting the client.

### Managing the services

Stop the services:

```bash
docker compose down
```

View service logs:

```bash
docker compose logs -f
```

Rebuild the images after changing application code or dependencies:

```bash
docker compose up --build
```

## Configuration

`.env.example` documents all required variables, including:

- Challenge credentials and flags
- Flask host, port, and debug settings
- Flask session secret
- Blind-SQL token, flag, host, port, and timeout

The Compose file loads `.env` into both services. Keep production or seminar-specific values outside version control.

## Contributing

Contributions are welcome. Please create a feature branch, keep changes focused, update relevant documentation, and verify the Docker Compose setup before opening a pull request.

## License

No explicit license has been specified for this repository. Contact the project maintainers before redistributing or reusing the materials.
