# Marketplace Monitoring Bot

<p align="left">
<a href="https://github.com/ilarionkuleshov/marketplace-monitoring-bot/actions/workflows/code-quality.yml/?query=event%3Apush+branch%3Amain">
    <img src="https://github.com/ilarionkuleshov/marketplace-monitoring-bot/actions/workflows/code-quality.yml/badge.svg?event=push&branch=main">
</a>
</p>

Bot for monitoring new adverts on marketplaces.


## Usage
Build the docker image:
```bash
docker build --build-arg UID={your-uid} --build-arg GID={your-gid} -t marketplace-monitoring-bot:latest .
```

Create `.env` file and fill it in according to the `.env.example` file.

Run docker compose services:
```bash
docker compose up -d
```
