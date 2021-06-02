# -*- coding: utf-8 -*-
import sqlite3
from DBUtils.PersistentDB import PersistentDB


class db_class():

    def __init__(self, thread_count: int = 1):
        self.pool = self.create_pool(thread_count)

    # 创建连接池
    def create_pool(self, thread_count: int):
        db_path = './db.db'
        pool = PersistentDB(sqlite3, maxusage=thread_count + 1, database=db_path)
        return pool

    # 插入备份数据
    def insert(self, sku: str):
        try:
            conn = self.pool.connection()
            cusr = conn.cursor()
            sql = "INSERT INTO datas VALUES('%s');" % sku
            cusr.execute(sql)
            conn.commit()
            return cusr.rowcount
        except Exception as e:
            return None
        finally:
            cusr.close()
            conn.close()

    # 查询列表
    def select_list(self):
        try:
            conn = self.pool.connection()
            cusr = conn.cursor()
            sql = "select distinct uid from datas;"
            cusr.execute(sql)
            values = cusr.fetchall()
            return values
        except Exception as e:
            print(e)
        finally:
            cusr.close()
            conn.close()

    # 查询相关搜索数据表
    def select_data(self, uid):
        try:
            conn = self.pool.connection()
            cusr = conn.cursor()
            sql = "select `index`,key,word,pv,pv_pc,pv_mob from datas where uid='%s';" % (uid)
            cusr.execute(sql)
            values = cusr.fetchall()
            return values
        except Exception as e:
            print(e)
        finally:
            cusr.close()
            conn.close()

    # 删除数据
    def delete(self, uid):
        try:
            conn = self.pool.connection()
            conn.isolation_level = None
            cusr = conn.cursor()
            sql = 'DELETE FROM datas WHERE uid = "%s";' % uid
            cusr.execute(sql)
            conn.commit()
            cusr.execute("VACUUM")
            conn.commit()
            return cusr.rowcount
        except Exception as e:
            print(e)
        finally:
            cusr.close()
            conn.close()

    # 删除数据
    def all_delete(self):
        try:
            conn = self.pool.connection()
            conn.isolation_level = None
            cusr = conn.cursor()
            sql = "DELETE FROM datas;"
            cusr.execute(sql)
            conn.commit()
            cusr.execute("VACUUM")
            conn.commit()
            return cusr.rowcount
        except Exception as e:
            print(e)
        finally:
            cusr.close()
            conn.close()

if __name__ == '__main__':
    db = db_class()
    db.all_delete()