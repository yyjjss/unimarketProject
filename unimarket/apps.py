from django.apps import AppConfig


class UnimarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unimarket'
    
    # 일주일이상된 상품, 공지사항 알림 스케줄러 시작
    def ready(self):
        from itemMarkUpdater import updater
        updater.start()
