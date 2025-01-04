set -e

pybabel extract --input-dirs=src/bot/ -o src/bot/locales/messages.pot
pybabel update -d src/bot/locales -D messages -i src/bot/locales/messages.pot
