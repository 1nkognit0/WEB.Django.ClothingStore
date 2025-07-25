from django.db import models
from users.models import User

class Orders(models.Model):
    CREATED = 0
    PAID = 1
    ON_WAY = 2
    DELIVERED = 3
    STATUSES = ((CREATED, 'Создан'),
                (PAID, 'Оплачен'),
                (ON_WAY, 'В пути'),
                (DELIVERED, 'Доставлен'),
    )
    first_name = models.CharField(max_length=55)
    last_name = models.CharField(max_length=55)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    busket_history = models.JSONField(default=dict)
    status = models.SmallIntegerField(default=CREATED, choices=STATUSES)
    initiator = models.ForeignKey(to=User, on_delete=models.CASCADE)

    def __str__(self):
        return (f'Номер заказа {self.id} '
                f'для {self.last_name, self.first_name}, инициирован пользователем {self.initiator}')
