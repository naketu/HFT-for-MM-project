import psycopg2
from config import user, host, db_name
import time
from datetime import datetime
from tinkoff.invest import Client

token = "t.EmsMWh-ufRjkccG8j5Az5tLqswa9FzFvhw2SUI7UL-hP_0m6T4-L8v12OgQbThJtVEaoru8jR792qtukZOaYAQ"
acc_id = '2056883362'

figi_usd = "BBG0013HGFT4"
figi_Tesla = "BBG000N9MNX3"
figi_Microsoft = "BBG000BPH459"

"""   Supportive functions   """


def convert(MoneyValue):
    price = MoneyValue.units + (MoneyValue.nano / 10**9)
    return price


"""   Execution of SQL requests   """


class SQL_manager():
    def __init__(self):
        try:
            connection = psycopg2.connect(host=host, user=user, database=db_name)
            connection.autocommit = True
            cursor = connection.cursor()

            self.connection = connection
            self.cursor = cursor

        except:
            raise Exception("no connection")
            self.connection = None
            self.cursor = None

    def insert(self, table: str, fields: str, values: str):
        command = "INSERT INTO " + table + " " + fields + " VALUES " + values + ";"
        # print(command)
        self.cursor.execute(command)

    def get_table(self, table: str):
        self.cursor.execute("select * from " + table + ";")
        table_data = self.cursor.fetchall()
        return table_data

    def execute_request(self, request: str):
        try:
            self.cursor.execute(request)
        except:
            print("command was corrupted")
            return 0

        try:
            response = self.cursor.fetchall()
            return(response)
        except:
            print("no output")

    def __del__(self):
        if self.cursor == None:
            pass
        else:
            self.cursor.close()
            self.connection.close()


"""   Collecting data   """

def data_collection():
    sql_manager = SQL_manager()

    id_counter = sql_manager.execute_request("SELECT MAX(id) from lob;")[0][0]

    if id_counter != None:
        id_counter = int(id_counter)
    else:
        id_counter = 0

    print("initial id: %d" % id_counter)

    with Client(token) as client:

        time_c = 0
        wanted_depth = 20
        print(time_c)

        while time_c < 60000:

            print("colecting data ... %d s" % time_c)
            try:
                LOB_response = client.market_data.get_order_book(figi=figi_usd, depth=wanted_depth)

            except:
                print("Warning - LOB data unavailable")
                # raise Exception("LOB data unavailable")

            try:
                id_counter += 1
                time_data = datetime.now()

                asks_data = LOB_response.asks
                bids_data = LOB_response.bids

                str_data = [str(id_counter), "'" + str(LOB_response.figi) + "'", str(LOB_response.depth),
                            "'" + str(time_data)[:19] + "'"]

                lob_data_str = "(" + str_data[0] + ", " + str_data[1] + ", " + str_data[2] + ", " + str_data[3] + ")"
                sql_manager.insert("lob", "(id, figi, depth, datetime)", lob_data_str)

                for data_line in asks_data:
                    price_data = convert(data_line.price)
                    str_asks_data = [str(id_counter), str(price_data), str(data_line.quantity),
                                     "'" + str(time_data)[:19] + "'"]
                    asks_data_line = "(" + str_asks_data[0] + ", " + str_asks_data[1] + ", " + str_asks_data[2] + ", " + \
                                     str_asks_data[3] + ")"
                    sql_manager.insert("asks", "(id, price, quantity, timedata)", asks_data_line)

                for data_line in bids_data:
                    price_data = convert(data_line.price)
                    str_bids_data = [str(id_counter), str(price_data), str(data_line.quantity),
                                     "'" + str(time_data)[:19] + "'"]
                    bids_data_line = "(" + str_bids_data[0] + ", " + str_bids_data[1] + ", " + str_bids_data[2] + ", " + \
                                     str_bids_data[3] + ")"
                    sql_manager.insert("bids", "(id, price, quantity, timedata)", bids_data_line)

            except:
                print("data insertion ended with an error")
                raise Exception("INSERT was corrupted")

            time.sleep(0.6)
            time_c += 0.6

    del sql_manager
    print("data collecting was complete")



