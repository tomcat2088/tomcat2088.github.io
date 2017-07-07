#!env python
# -*- coding: UTF-8 -*-

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import jianshusummary
import subprocess

subprocess.call(['osascript', '-e', 'display notification "日常任务后台已启动" with title "日常任务"'])

# 输出时间
def job():
    subprocess.call(['osascript', '-e', 'display notification "正在刷新简书数据" with title "日常任务"'])
    if jianshusummary.processJianshuSummary():
        subprocess.call(['osascript', '-e', 'display notification "成功刷新简书数据" with title "日常任务"'])
        subprocess.call(['zsh', './publish.sh'])
# BlockingScheduler
scheduler = BlockingScheduler()
scheduler.add_job(job, 'cron', day_of_week='1-7', hour=14, minute=7)
scheduler.start()
