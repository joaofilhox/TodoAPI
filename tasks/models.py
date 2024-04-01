from django.db import models

class Task(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        "accounts.Account",
        on_delete=models.CASCADE,
        related_name="tasks",
        null=True,
    )

    def __str__(self):
        return self.title

