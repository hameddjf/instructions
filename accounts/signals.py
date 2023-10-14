from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def assign_group(sender, instance, created, **kwargs):
    if created:
        if instance.is_behvarz:
            group = Group.objects.get(name="بهورزان")
            instance.groups.add(group)
        elif instance.is_staff:
            group = Group.objects.get(name="مدیران")
            instance.groups.add(group)
        elif instance.is_superuser:
            group = Group.objects.get(name="ادمین")
            instance.groups.add(group)
        else:
            group = Group.objects.get(name="کارشناسان")
            instance.groups.add(group)
