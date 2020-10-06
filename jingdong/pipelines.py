from itemadapter import ItemAdapter


import json
import pymysql

class JingdongPipeline(object):
    """
    json存储
    """
    def __init__(self):
        # 打开文件
        self.file = open('jd.json', 'w', encoding='utf-8')

    # 该方法用于处理数据
    def process_item(self, item, spider):
        # 读取item中的数据
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        # 写入文件
        self.file.write(line)
        # 返回item
        return item

    # 该方法在spider被开启时被调用。
    def open_spider(self, spider):
        pass

    # 该方法在spider被关闭时被调用。
    def close_spider(self, spider):
        pass


class MysqlPipeline:
    """
    MySQL存储
    """
    def __init__(self, host, database, user, password, port):
        self.host = 'localhost'
        self.database = 'test'
        self.user = 'root'
        self.password = 'mysql'
        self.port = 3306
        self.db = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        """
        配置数据库
        """
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        '''
        连接数据库
        '''
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8', port=self.port)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        """
        插入数据
        """
        data = dict(item)
        table = 'jd'
        keys = ','.join(data.keys())
        values = ','.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item

    def close_spider(self, spider):
        """
        关闭数据库
        """
        self.db.close()