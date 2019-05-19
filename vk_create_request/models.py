from django.db import models


class VKGROUP(models.Model):
    id_group = models.CharField(max_length=100, unique=True, verbose_name='ID Группы')

    @property
    def __str__(self):
        return self.id_group
    class Meta:
        ordering = ['id_group']
        verbose_name = 'Группа ВК'
        verbose_name_plural = 'Группы ВК'


class VKGROUPREQUESTS(models.Model):
    id_group = models.CharField(max_length=100)
    count_posts = models.IntegerField()
    date_time_request = models.DateTimeField(auto_now_add=True)
    file_path = models.FilePathField(blank=True)

    @property
    def __str_(self):
        return self.id_group

    class Meta:
        ordering = ['date_time_request']
        verbose_name = 'Запрос'
        verbose_name_plural = 'Запрос на парсинг'