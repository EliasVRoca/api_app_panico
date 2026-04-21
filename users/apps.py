from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from django.db.models.signals import post_migrate
        post_migrate.connect(_create_default_admin, sender=self)


def _create_default_admin(sender, **kwargs):
    """
    Crea o actualiza el superusuario 'admin' despues de cada migracion.
    Credenciales por defecto:
        username : admin
        email    : admin@admin.com
        password : admin
    """
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        email    = 'admin@admin.com'
        username = 'admin'
        password = 'admin'

        user, created = User.objects.get_or_create(
            email=email,
            defaults=dict(
                username=username,
                is_staff=True,
                is_superuser=True,
                is_active=True,
            )
        )

        # Always ensure password and flags are up to date
        user.username     = username
        user.is_staff     = True
        user.is_superuser = True
        user.is_active    = True
        user.set_password(password)
        user.save()

        if created:
            print(f"\n  [✔] Superusuario '{username}' creado (email: {email}, password: {password})")
        else:
            print(f"\n  [✔] Superusuario '{username}' ya existe — credenciales verificadas.")

    except Exception as e:
        # Silently ignore errors during early setup (DB may not exist yet)
        pass
