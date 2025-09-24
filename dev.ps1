Start-Process powershell -ArgumentList "-Command", "mongod --dbpath ./dbs/mongo/"
Start-Process powershell -ArgumentList "-Command", "cd dbs/redis; ./redis/redis-server"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd apps/api-crawler; .venv/Scripts/Activate.ps1;"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd apps/notify-bot; .venv/Scripts/Activate.ps1;"