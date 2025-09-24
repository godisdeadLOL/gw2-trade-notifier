import asyncio
import schedule
import time

from scripts.sync_users import sync_users


def job():
    print("syncing users")
    asyncio.run(sync_users())


schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
