# 数据库初始化

## 本地环境

DATABASE=mysql://gymall:local-gymall@127.0.0.1:3306/gymall


```mysql
create user 'gymall'@'%' identified by 'local-gymall';

create database gymall character set utf8mb4 collate utf8mb4_general_ci;
create database test_gymall character set utf8mb4 collate utf8mb4_general_ci;

grant all privileges on gymall.* to 'gymall'@'%';
grant all privileges on test_gymall.* to 'gymall'@'%';
```
