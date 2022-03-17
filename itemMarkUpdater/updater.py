from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .itemMarkApi import updateItemMark, updateCategoryModel, updateCheckModel

# apscheduler 실행 함수
def start():
    scheduler = BackgroundScheduler()
    # 매일 24:00
    scheduler.add_job(updateItemMark, 'cron', hour=0, minute=0)
    # 매주 금요일 24:00
    scheduler.add_job(updateCategoryModel, 'cron', day_of_week='fri', hour=0, minute=0)
    # 매달 3주째 금요일 24:00
    scheduler.add_job(updateCheckModel, 'cron', month='1-12', day='3rd fri', hour=0, minute=0)
    scheduler.start()