from django.conf import settings
from django.db import models

from employees.models import Employee
from bot.bot import bot_init

def news_photo_path(instance, filename):
    return f"news/{filename}"


class News(models.Model):
    class Meta:
        ordering = ("-id", )
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'

    employee = models.ForeignKey(
        Employee,
        related_name="created_news",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    all_employees = models.BooleanField(default=False)
    employees_to_notify = models.ManyToManyField(
        Employee, related_name="news_in_notification")
    employees_notified = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=news_photo_path)
    date_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        init_id = self.id
        super(News, self).save(*args, **kwargs)
        if not self.employees_notified:
            employees = self.employees_to_notify.all()
            if self.all_employees:
                employees = Employee.objects.all()
            if employees.exists():
                updater = bot_init(settings.BOT_TOKEN)
                updater.news_notify(self, employees)
                self.employees_notified = True
                self.save()
