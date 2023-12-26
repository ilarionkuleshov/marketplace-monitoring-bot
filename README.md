# Marketplace Monitoring Bot
Telegram bot for monitoring adverts through search queries on marketplaces.

## Building
Create and fill out `.env` file:
```
cp .env.example .env
```
Run the build using `docker compose`:
```
docker compose build
```

## Usage
For development, run these services:
```
docker compose up -d python postgres rabbitmq
```
