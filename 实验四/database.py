import pymysql

class mydatabase():
    def __init__(self):
        self.conn=pymysql.connect(
            host='localhost',
            port=3306, 
            user='root',
            password='ttn991122',
            db='dhtdatabase',
            charset='utf8'
        )
        
    def myselect(self, select_id):
        cursor = self.conn.cursor()
        sql = 'select count(*) from dht_node where node_id = "%s"' % select_id
        cursor.execute(sql)
        if (cursor.fetchone()[0] == 0):
            print('node with id = %s NOT FOUND' % select_id)
        else:
            sql = 'select * from dht_node where node_id = "%s"' % select_id
            cursor.execute(sql)
            node = tuple(cursor.fetchone())
            cursor.close()
            return node
    
    def myinsert(self, insert_id, insert_ip, insert_port):
        cursor = self.conn.cursor()
        print(insert_id.hex())
        print(type(insert_id.hex()))
        sql = 'select count(*) from dht_node where node_id = "%s"' % insert_id.hex()
        cursor.execute(sql)
        if (cursor.fetchone()[0] == 0):
            sql = 'insert into dht_node(node_id, node_ip, node_port) values("%s", "%s", "%s")' % (insert_id.hex(), insert_ip, str(insert_port))
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        else:
            print("node with id = %s FOUND, don't insert"% insert_id.hex())

    def myclose(self):
        self.conn.close()