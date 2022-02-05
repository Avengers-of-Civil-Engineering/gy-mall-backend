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
                ('phone_number', models.CharField(blank=True, max_length=191, null=True, unique=True, verbose_name='手机号码')),
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
                ('desc', models.CharField(blank=True, max_length=191, verbose_name='图片备注')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '图片',
                'verbose_name_plural': '图片',
            },
        ),
        migrations.CreateModel(
            name='Merchant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='商户名')),
                ('express_limit', models.IntegerField(default=0, verbose_name='起送运费')),
                ('express_price', models.IntegerField(default=0, verbose_name='基础运费')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('slogan', models.CharField(blank=True, max_length=191, verbose_name='促销文字说明')),
                ('rank', models.IntegerField(db_index=True, default=999, verbose_name='排序(大->小)')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('img', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.appimage')),
            ],
            options={
                'verbose_name': '商户',
                'verbose_name_plural': '商户',
                'ordering': ('-rank',),
            },
        ),
        migrations.CreateModel(
            name='MerchantProductsTab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='类目名')),
                ('slug', models.CharField(max_length=191, verbose_name='slug')),
                ('rank', models.IntegerField(db_index=True, default=999, verbose_name='排序(大->小)')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tabs', to='mall.merchant', verbose_name='商户')),
            ],
            options={
                'verbose_name': '类目',
                'verbose_name_plural': '类目',
                'ordering': ('-rank',),
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.CharField(default=mall.models.get_order_id, editable=False, max_length=64, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('creating', '创建中'), ('waiting_to_pay', '待支付'), ('paid_succeed', '支付成功'), ('unpaid_closed', '未支付关闭'), ('sending', '快递发送中'), ('finished', '已完成')], max_length=191)),
                ('price_total', models.DecimalField(blank=True, decimal_places=2, max_digits=14, verbose_name='订单总价')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191, verbose_name='商品名')),
                ('unit_desc', models.CharField(blank=True, max_length=191, verbose_name='单位文字')),
                ('old_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='初始单价')),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='当前单价')),
                ('sales', models.IntegerField(default=0, verbose_name='销量')),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('img', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.appimage')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='mall.merchant', verbose_name='商户')),
                ('tab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='mall.merchantproductstab', verbose_name='所属类目')),
            ],
            options={
                'verbose_name': '商品',
                'verbose_name_plural': '商品',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, verbose_name='实际单价')),
                ('quantity', models.IntegerField(verbose_name='数量')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='mall.order', verbose_name='订单')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='mall.product', verbose_name='商品')),
            ],
            options={
                'verbose_name': '订单项',
                'verbose_name_plural': '订单项',
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
