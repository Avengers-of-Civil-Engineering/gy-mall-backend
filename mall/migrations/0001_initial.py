# Generated by Django 3.2.11 on 2022-02-05 13:31

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import mall.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(blank=True, max_length=191, null=True, unique=True, verbose_name='????????????')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AppImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('img', models.ImageField(height_field='height', upload_to='', width_field='width')),
                ('desc', models.CharField(blank=True, max_length=191, verbose_name='????????????')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '??????',
                'verbose_name_plural': '??????',
            },
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='?????????')),
                ('express_limit', models.IntegerField(default=0, verbose_name='????????????')),
                ('express_price', models.IntegerField(default=0, verbose_name='????????????')),
                ('sales', models.IntegerField(default=0, verbose_name='??????')),
                ('slogan', models.CharField(blank=True, max_length=191, verbose_name='??????????????????')),
                ('rank', models.IntegerField(db_index=True, default=999, verbose_name='??????(???->???)')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('img', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.appimage')),
            ],
            options={
                'verbose_name': '??????',
                'verbose_name_plural': '??????',
                'ordering': ('-rank',),
            },
        ),
        migrations.CreateModel(
            name='MerchantProductsTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='?????????')),
                ('slug', models.CharField(max_length=191, verbose_name='slug')),
                ('rank', models.IntegerField(db_index=True, default=999, verbose_name='??????(???->???)')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tabs', to='mall.merchant', verbose_name='??????')),
            ],
            options={
                'verbose_name': '??????',
                'verbose_name_plural': '??????',
                'ordering': ('-rank',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.CharField(default=mall.models.get_order_id, editable=False, max_length=64, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('creating', '?????????'), ('waiting_to_pay', '?????????'), ('paid_succeed', '????????????'), ('unpaid_closed', '???????????????'), ('sending', '???????????????'), ('finished', '?????????')], max_length=191)),
                ('price_total', models.DecimalField(blank=True, decimal_places=2, max_digits=14, verbose_name='????????????')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='??????')),
            ],
            options={
                'verbose_name': '??????',
                'verbose_name_plural': '??????',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='?????????')),
                ('unit_desc', models.CharField(blank=True, max_length=191, verbose_name='????????????')),
                ('old_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='????????????')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='????????????')),
                ('sales', models.IntegerField(default=0, verbose_name='??????')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('img', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.appimage')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='mall.merchant', verbose_name='??????')),
                ('tab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='mall.merchantproductstab', verbose_name='????????????')),
            ],
            options={
                'verbose_name': '??????',
                'verbose_name_plural': '??????',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, verbose_name='????????????')),
                ('quantity', models.IntegerField(verbose_name='??????')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='mall.order', verbose_name='??????')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.product', verbose_name='??????')),
            ],
            options={
                'verbose_name': '?????????',
                'verbose_name_plural': '?????????',
            },
        ),
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mall.appimage'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AddConstraint(
            model_name='merchantproductstab',
            constraint=models.UniqueConstraint(fields=('merchant', 'slug'), name='unique-merchant-slug'),
        ),
    ]
