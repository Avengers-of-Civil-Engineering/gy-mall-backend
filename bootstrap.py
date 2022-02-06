from gymall.read_env import read_env
import MySQLdb
import multiprocessing
import subprocess
import sys

env = read_env()


def get_db_conn():
    db_config = env.db("DATABASE_URL")

    conn = MySQLdb.Connection(
        host=db_config['HOST'],
        port=db_config['PORT'],
        user=db_config['USER'],
        password=db_config['PASSWORD'],
    )

    return conn


def setup_mysql_db():
    conn = get_db_conn()
    cursor = conn.cursor()

    cursor.execute("create database if not exists gymall character set utf8mb4 collate utf8mb4_general_ci;")
    cursor.execute("create database if not exists test_gymall character set utf8mb4 collate utf8mb4_general_ci;")

    cursor.close()
    conn.close()


def setup_mysql_table():
    cmd = f"python3 manage.py migrate --noinput"
    print("call cmd:", cmd, file=sys.stderr)
    subprocess.call(cmd, shell=True)


def run_collectstatic():
    cmd = "python3 manage.py collectstatic --no-input"
    print("call cmd:", cmd, file=sys.stderr)
    subprocess.call(cmd, shell=True)


def run_server():
    worker_num = 2 * multiprocessing.cpu_count() + 1
    cmd = f"gunicorn gymall.wsgi -w {worker_num} -b 0.0.0.0:8000 -k gthread --threads 8"
    print("call cmd:", cmd, file=sys.stderr)
    subprocess.call(cmd, shell=True)


setup_mysql_db()

setup_mysql_table()

run_collectstatic()

run_server()
