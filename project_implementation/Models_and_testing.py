import time
from tinkoff.invest import Client, MoneyValue, OrderDirection, OrderType, Quotation
from sql_work import SQL_manager

"""   Personal info!!!   """

token = "t.some_characters"
sandbox_token = "t.some_other_characters"
acc_id = 'some_number'

figi_usd = "BBG0013HGFT4"  #BBG000BWPXQ8
figi_Microsoft = "BBG000BPH459"
figi_Tesla = "BBG000N9MNX3"

"""   Supportive functions   """


def convert_price(MoneyValue):
    price = MoneyValue.units + (MoneyValue.nano / 10**9)
    return price


def convert_to_MoneyValue(price, currency='rub'):
    units = price // 1
    nano = (price % 1) * 10**9
    return MoneyValue(units=units, nano=nano, currency=currency)


def get_LOB_data(figi_0=figi_usd):

    with Client(token) as client:
        LOB = client.market_data.get_order_book(figi=figi_0, depth=50)

        ask_price = convert_price(LOB.asks[0].price)
        bid_price = convert_price(LOB.bids[0].price)

        q_a = 0
        q_b = 0

        for line in LOB.asks:
            q_a += line.quantity
        for line in LOB.bids:
            q_b += line.quantity

        # print(q_b, q_a)
        # print(bid_price, ask_price)

        return ((q_b, q_a), (bid_price, ask_price))


def convert_to_Quotation(price):
    units = int(price // 1)
    nano = int((price % 1) * 10**9)
    return Quotation(units=units, nano=nano)


"""   Models   """


class model_1:
    def __init__(self):
        self.cur_best_bid_price = 0
        self.cur_best_ask_price = 0

        self.last_best_bid_price = 0
        self.last_best_ask_price = 0

        self.bid_quantity = 0
        self.ask_quantity = 0

        self.ask_price = 0
        self.bid_price = 0

        self.increment = 0.1
        self.parameter = 0.5 #default parameter value
        self.state = 0

        self.colors = dict()
        self.color_match = dict()

        self.colors["red"] = "\033[1;31m"
        self.colors["green"] = "\033[1;32m"
        self.colors["blue"] = "\033[1;34m"
        self.colors["clear"] = "\033[0;0;m"

        self.color_match[0] = self.colors["blue"]
        self.color_match[1] = self.colors["green"]
        self.color_match[-1] = self.colors["red"]

    def set_parameters(self, param=0.5, increm=0.1):
        self.parameter = param
        self.increment = increm

    def update_prices_b_a(self, bid_price, ask_price):

        self.last_best_bid_price = self.cur_best_bid_price
        self.last_best_ask_price = self.cur_best_ask_price

        self.cur_best_bid_price = bid_price
        self.cur_best_ask_price = ask_price

        self.increment = (ask_price - bid_price) / 2

    def update_LOB_data_b_a(self, b_q, a_q):
        self.bid_quantity = b_q
        self.ask_quantity = a_q

    def last_im_strategy(self):
        value_1 = self.bid_quantity - self.ask_quantity
        value_2 = -value_1
        value_3 = self.ask_quantity + self.bid_quantity

        last_price = (self.cur_best_ask_price + self.cur_best_bid_price)/2

        if value_1/value_3 > self.parameter: #(qb -qs)/(qb +qs)>0.5
            self.ask_price = last_price + self.increment * 2
            self.bid_price = last_price
            self.state = 1

        elif value_2/value_3 > self.parameter: #(qs –qb)/(qb +qs) >0.5
            self.ask_price = last_price
            self.bid_price = last_price - self.increment * 2
            self.state = -1

        else:
            self.ask_price = last_price + self.increment
            self.bid_price = last_price - self.increment
            self.state = 0

        print(self.color_match[self.state], end="")
        print("last+im strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])

        return (self.bid_price, self.ask_price)

    def last_im_v_strategy(self):
        value_1 = self.bid_quantity - self.ask_quantity
        value_2 = -value_1
        value_3 = self.ask_quantity + self.bid_quantity

        last_price = (self.cur_best_ask_price + self.cur_best_bid_price) / 2
        previous_price = (self.last_best_ask_price + self.last_best_bid_price) / 2

        price_change = abs(last_price - previous_price)

        if value_1 / value_3 > self.parameter:  # (qb -qs)/(qb +qs)>0.5
            self.ask_price = last_price + (price_change + 2) * self.increment
            self.bid_price = last_price - price_change * self.increment
            self.state = 1


        elif value_2 / value_3 > self.parameter:  # (qs –qb)/(qb +qs) >0.5
            self.ask_price = last_price + price_change * self.increment
            self.bid_price = last_price - (price_change + 2) * self.increment
            self.state = -1


        else:
            self.ask_price = last_price + (price_change + 1) * self.increment
            self.bid_price = last_price - (price_change + 1) * self.increment
            self.state = 0


        print(self.color_match[self.state], end="")
        print("last+im+v strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])


        return (self.bid_price, self.ask_price)


class model_2:
    def __init__(self):
        self.cur_best_bid_price = 0
        self.cur_best_ask_price = 0

        self.last_best_bid_price = 0
        self.last_best_ask_price = 0

        self.bid_quantity = 0
        self.ask_quantity = 0

        self.ask_price = 0
        self.bid_price = 0

        self.r_h = 0
        self.r_m = 0

        self.increment_1 = 0.1
        self.increment_2 = 2 * self.increment_1
        self.parameter = 0.5 #default parameter value
        self.state = 0

        self.colors = dict()
        self.color_match = dict()

        self.colors["red"] = "\033[1;31m"
        self.colors["green"] = "\033[1;32m"
        self.colors["blue"] = "\033[1;34m"
        self.colors["clear"] = "\033[0;0;m"

        self.color_match[0] = self.colors["blue"]
        self.color_match[1] = self.colors["green"]
        self.color_match[-1] = self.colors["red"]

    def set_parameters(self, param=0.5, increm1=0.1, increm2=0.2):
        self.parameter = param
        self.increment_1 = increm1
        self.increment_2 = increm2

    def update_prices_b_a(self, bid_price, ask_price):

        self.last_best_bid_price = self.cur_best_bid_price
        self.last_best_ask_price = self.cur_best_ask_price

        self.cur_best_bid_price = bid_price
        self.cur_best_ask_price = ask_price

        if self.state == 0:
            self.increment_1 = (ask_price - bid_price)
        else:
            self.increment_2 = (ask_price - bid_price)


    def update_rates_m_h(self, r_m, r_h):
        self.r_h = r_h
        self.r_m = r_m

    def calculate_quantity_1(self):
        if self.state==0:
            #passive
            if self.r_m == 0 and self.r_h == 0:
                q = min(self.bid_quantity, self.ask_quantity)
            elif self.r_m == 0:
                q = min(self.bid_quantity, self.ask_quantity) * self.r_h
            else:
                q = min(self.bid_quantity, self.ask_quantity) * (self.r_h + self.r_m) * 0.5

        else:
            #aggressive
            if self.r_m == 0 and self.r_h == 0:
                q = abs(self.bid_quantity - self.ask_quantity)
            elif self.r_m == 0:
                q = abs(self.bid_quantity - self.ask_quantity) * self.r_h
            else:
                q = abs(self.bid_quantity - self.ask_quantity) * (self.r_h + self.r_m) * 0.5

        return int(q)


    def update_LOB_data_b_a(self, b_q, a_q):
        self.bid_quantity = b_q
        self.ask_quantity = a_q

    def best_bid_ask(self):
        self.ask_price = self.cur_best_ask_price
        self.bid_price = self.cur_best_bid_price

        print(self.colors["clear"], end="")
        print("best ask/bid strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])

        return (self.bid_price, self.ask_price)

    def last_and_along(self):
        value_1 = self.bid_quantity - self.ask_quantity
        value_2 = -value_1
        value_3 = self.ask_quantity + self.bid_quantity

        last_price = (self.cur_best_ask_price + self.cur_best_bid_price) / 2

        if value_1 / value_3 > self.parameter:  # (qb - qs)/(qb + qs)>0.5
            self.ask_price = last_price + self.increment_2
            self.bid_price = last_price
            self.state = 1


        elif value_2 / value_3 > self.parameter:  # (qs – qb)/(qb + qs) >0.5
            self.ask_price = last_price
            self.bid_price = last_price - self.increment_2
            self.state = -1


        else:
            self.ask_price = last_price + self.increment_1 / 2
            self.bid_price = last_price - self.increment_1 / 2
            self.state = 0


        print(self.color_match[self.state], end="")
        print("last + along strategy")
        print("signals: ----", end=' ')
        print(self.bid_price, self.ask_price, sep=" : ", end='')
        print(self.colors["clear"])


        return (self.bid_price, self.ask_price)


"""   Testers   """
#     sandbox


def create_new_account(balance=0, currency='rub'):
    amount = convert_to_MoneyValue(balance, currency)

    with Client(token=sandbox_token) as client:
        new_acc_id = client.sandbox.open_sandbox_account().account_id
        print("New Account has id :", new_acc_id)
        client.sandbox.sandbox_pay_in(
            account_id=new_acc_id,
            amount=amount
        )

    return new_acc_id


def delete_account(acc_id):
    with Client(token=sandbox_token) as client:
        client.sandbox.close_sandbox_account(account_id=acc_id)


class SandboxTester:
    def __init__(self, account_id, token, figi, model_type,
                 limit_quantity=10000000, limit_percentage=100, iterations=1000, debt=0, tax=0):
        model_types = dict()

        model_types["last_im_strategy"] = 1
        model_types["last_im_v_strategy"] = 2
        model_types["ask_bid_strategy"] = 3
        model_types["last_along_strategy"] = 4

        if model_types[model_type] is None:
            raise Exception("Model type does not exist. Existing types:"
                            "last_im_strategy, last_im_v_strategy for model_1,"
                            "ask_bid_strategy, last_along_strategy for model_2")
        else:
            self.model_type = model_types[model_type]
            if self.model_type < 3:
                model = model_1()
            else:
                model = model_2()

        self.model = model
        self.account_id = account_id
        self.token = token
        self.working_figi = figi
        self.limit_quantity = limit_quantity
        self.limit_percentage = limit_percentage
        self.iterations = iterations
        self.debt = debt
        self.tax = tax

        with Client(token=self.token) as client:
            client_sb = client.sandbox

            self.moneeey = client_sb.get_sandbox_portfolio(account_id=self.account_id).total_amount_currencies
            time.sleep(0.6)

            self.money_float = convert_price(self.moneeey)
            max_quantity = convert_price(self.moneeey)
            last_price = client.market_data.get_last_prices(figi=[self.working_figi]).last_prices[0].price
            time.sleep(0.6)

            self.last_price = convert_price(last_price)
            self.max_quantity = max_quantity // self.last_price

        self.cur_balance = self.money_float

    def model_run(self):

        if self.model_type == 1:
            return self.model.last_im_strategy()
        elif self.model_type == 2:
            return self.model.last_im_v_strategy()
        elif self.model_type == 3:
            return self.model.best_bid_ask()
        elif self.model_type == 4:
            return self.model.last_and_along()
        else:
            return None

    def update_balance(self):
        last_balance = self.cur_balance

        with Client(token=self.token) as client:
            client_sb = client.sandbox
            response = client_sb.get_sandbox_portfolio(account_id=self.account_id)
            self.cur_balance = response.total_amount_currencies
            quantity = convert_price(response.positions[0].quantity)
            self.cur_balance = convert_price(self.cur_balance)
            self.debt = (self.cur_balance - last_balance) * self.tax
            print(self.cur_balance)
            # print(self.cur_balance, "  :  ", quantity)
            print("////////")
            time.sleep(0.6)
            # print(client_sb.get_sandbox_portfolio(account_id=self.account_id))

    def place_order_ask(self, price, quantity, time_c=0):
        if time_c > 3:
            return "ASK order was NOT EXECUTED"

        try:
            with Client(token=self.token) as client:
                r = client.sandbox.post_sandbox_order(
                    figi=self.working_figi,
                    price=price,
                    x_app_name="naketu.HFT",
                    quantity=quantity,
                    account_id=self.account_id,
                    order_id="sfkjhsf234897kjsdfh8has8dy3827gdslu[]" + str(time.localtime()),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )

            time.sleep(0.6)
            return r

        except:
            time.sleep(0.6)
            time_c += 0.6

            print("ERROR OCCURED AT ASK POST ORDER, reposting...")

            r = self.place_order_bid(price, quantity, time_c)
            return r

    def place_order_bid(self, price, quantity, time_c=0):
        if time_c > 3:
            return "BID order was NOT EXECUTED"

        try:
            with Client(token=self.token) as client:

                r = client.sandbox.post_sandbox_order(
                    figi=self.working_figi,
                    price=price,
                    quantity=quantity,
                    account_id=self.account_id,
                    order_id="sfkjhsf234897kjsdfh8has8dy3827gdslu[]" + str(time.localtime()),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )

            time.sleep(0.6)
            return r

        except:
            time.sleep(0.6)
            time_c += 0.6

            print("ERROR OCCURED AT BID POST ORDER, reposting...")

            r = self.place_order_bid(price, quantity, time_c)
            return r

    def cancel_order(self, order_id):
        with Client(token=self.token) as client:
            try:
                r = client.sandbox.cancel_sandbox_order(
                    account_id=self.account_id,
                    order_id=order_id,
                )
                time.sleep(0.6)
            except:
                r = "ORDER IS NOT CANCELED"
            return r

    def check_orders(self, last_bid_price, bid_price, last_ask_price, ask_price):
        with Client(token=self.token) as client:
            orders = client.sandbox.get_sandbox_orders(account_id=self.account_id)
            time.sleep(0.6)

            if last_bid_price != bid_price and last_ask_price != ask_price:
                return orders.orders
            elif last_bid_price != bid_price:
                orders = [ord for ord in orders.orders if ord.direction == OrderDirection.ORDER_DIRECTION_BUY]
                return orders
            elif last_ask_price != ask_price:
                orders = [ord for ord in orders.orders if ord.direction == OrderDirection.ORDER_DIRECTION_SELL]
                return orders
            else:
                return []

    def test(self):
        time_c = 0

        last_bid_price = 0
        last_ask_price = 0

        try:
            old_LOB = get_LOB_data(self.working_figi)
            time.sleep(0.6)
        except:
            raise Exception("NO CONNECTION TO MARKET")

        for i in range(self.iterations):

            self.update_balance()

            try:
                LOB_data = get_LOB_data(self.working_figi)
            except:
                print("LOB does not responding")
                time.sleep(2)
                time_c += 2
                print("loading...", time_c)
                continue

            self.model.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
            self.model.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

            cur_price = (LOB_data[1][0] + LOB_data[1][1])/2

            response = self.model_run()

            bid_price = convert_to_Quotation(response[0])
            ask_price = convert_to_Quotation(response[1])

            orders = self.check_orders(last_bid_price, bid_price, last_ask_price, ask_price)

            if len(orders) != 0:
                for order in orders:
                    self.cancel_order(order.order_id)

            quantity = int(min(self.limit_percentage/100 * self.money_float,
                               self.limit_quantity, self.cur_balance // cur_price))

            print(self.place_order_ask(ask_price, quantity // 2),
                  self.place_order_bid(bid_price, quantity // 2))

            last_bid_price = bid_price
            last_ask_price = ask_price

            time.sleep(0.6)


#     backtest


class BackTester:
    def __init__(self):
        self.id = 0
        self.global_q = 0
        self.all_orders_q = 0
        self.asks = []
        self.bids = []
        self.lob = []
        self.balance = 0
        self.shares = 0
        self.limit_percentage = 100
        self.limit_percentage = 100000000

    def set_limits(self, percentage=100, quantity=100000000):
        self.limit_percentage = percentage
        self.limit_quantity = quantity

    def check_order_ask(self, price, quantity):
        flag = 0
        q = quantity

        line = 0

        sql_manager = SQL_manager()

        lob_data = sql_manager.execute_request(
            "select * from lob where figi='BBG0013HGFT4' and id>" + str(self.id) + " limit 1;"
        )[0]

        cur_id = lob_data[0]

        bids_data = sql_manager.execute_request(
            "select * from bids where id=" + str(cur_id) + " order by price desc;"
        )

        cur_price = bids_data[0][1]
        cur_id = 0

        while (q > 0) and (price <= cur_price) and (cur_id < len(bids_data)):
            if q > bids_data[cur_id][2]:
                q -= bids_data[cur_id][2]
                self.shares -= bids_data[cur_id][2]
                self.balance += bids_data[cur_id][1] * bids_data[cur_id][2]
                cur_id += 1
            else:
                self.shares -= q
                self.balance += (bids_data[cur_id][1] * q)
                q = 0
                cur_id += 1

        self.global_q += quantity - q

    def check_order_bid(self, price, quantity):
        flag = 0
        q = quantity

        line = 0

        sql_manager = SQL_manager()

        lob_data = sql_manager.execute_request(
            "select * from lob where figi='BBG0013HGFT4' and id>" + str(self.id) + " limit 1;"
        )[0]

        cur_id = lob_data[0]

        asks_data = sql_manager.execute_request(
            "select * from asks where id=" + str(cur_id) + " order by price asc;"
        )

        cur_price = asks_data[0][1]
        cur_id = 0

        while (q > 0) and (price >= cur_price) and (cur_id < len(asks_data)):
            if q > asks_data[cur_id][2]:
                q2 = asks_data[cur_id][2]
                q -= asks_data[cur_id][2]
                self.shares += asks_data[cur_id][2]
                self.balance -= (asks_data[cur_id][1] * asks_data[cur_id][2])
                cur_id += 1
            else:
                self.shares += q
                self.balance -= (asks_data[cur_id][1] * q)
                q = 0
                cur_id += 1

        self.global_q += quantity - q

    def get_LOB_data_test(self):
        q_b = 0
        q_a = 0
        bid_price = 0
        ask_price = 0
        sql_manager = SQL_manager()

        # data_size = sql_manager.execute_request("select count(*) from lob where figi='BBG0013HGFT4';")[0][0]

        lob_data = sql_manager.execute_request(
            "select * from lob where figi='BBG0013HGFT4' and id>" + str(self.id) + " limit 1;"
        )[0]

        cur_id = lob_data[0]

        asks_data = sql_manager.execute_request(
            "select * from asks where id=" + str(cur_id) + ";"
        )

        bids_data = sql_manager.execute_request(
            "select * from bids where id=" + str(cur_id) + ";"
        )

        ask_price = asks_data[0][1]
        bid_price = bids_data[0][1]

        for i in range(len(asks_data)):
            q_a += asks_data[i][2]
            q_b += bids_data[i][2]

        self.id += 1
        self.lob = lob_data
        self.asks = asks_data
        self.bids = bids_data

        del sql_manager
        return (q_b, q_a), (bid_price, ask_price)


class pool_of_orders:
    def __init__(self):
        self.asks = []
        self.bids = []


def update_orders(last_bid_price, bid_price, last_ask_price, ask_price, pool_of_orders):

    if last_bid_price != bid_price and last_ask_price != ask_price:
        return pool_of_orders
    elif last_bid_price != bid_price:
        pool_of_orders.bids = []
        return pool_of_orders
    elif last_ask_price != ask_price:
        pool_of_orders.asks = []
        return pool_of_orders
    else:
        return pool_of_orders


def ultimate_back_test(balance, iterations, model_type, figi=figi_usd):
    model_types = dict()

    model_types["last_im_strategy"] = 1
    model_types["last_im_v_strategy"] = 2
    model_types["ask_bid_strategy"] = 3
    model_types["last_along_strategy"] = 4

    if model_types[model_type] is None:
        raise Exception("Model type does not exist. Existing types:"
                        "last_im_strategy, last_im_v_strategy for model_1,"
                        "ask_bid_strategy, last_along_strategy for model_2")

    else:
        model_type = model_types[model_type]
        if model_type < 3:
            model = model_1()
        else:
            model = model_2()

    back_test = BackTester()
    back_test.balance = balance
    back_test.set_limits(10, 100000000)

    orders = pool_of_orders()

    data_size = SQL_manager().execute_request("select count(*) from lob where figi='BBG0013HGFT4';")[0][0]

    iterations = min(iterations, int(data_size))

    working_figi = figi

    old_LOB = back_test.get_LOB_data_test()
    print("start")

    last_bid_price = old_LOB[1][0]
    last_ask_price = old_LOB[1][0]

    for i in range(iterations):
        LOB_data = back_test.get_LOB_data_test()
        # clean_output()

        model.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
        model.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

        cur_price = (LOB_data[1][0] + LOB_data[1][1]) / 2

        # model_1 part:
        if model_type < 3:

            if model_type == 1:
                response = model.last_im_strategy()
            else:
                response = model.last_im_v_strategy()

            bid_price = response[0]
            ask_price = response[1]

            orders = update_orders(last_bid_price, bid_price, last_ask_price, ask_price, orders)

            quantity_bid = int(min(back_test.limit_percentage / 100 * back_test.balance,
                               back_test.limit_quantity, back_test.balance // cur_price))

            quantity_ask = int(min(back_test.limit_percentage / 100 * back_test.balance,
                                   back_test.limit_quantity))

            back_test.check_order_ask(ask_price, quantity_ask)
            back_test.check_order_bid(bid_price, quantity_bid)

            last_bid_price = bid_price
            last_ask_price = ask_price

            back_test.all_orders_q += quantity_bid + quantity_ask


        # model_2 part:
        else:

            if model_type == 3:
                response = model.best_bid_ask()
            else:
                response = model.last_and_along()

            bid_price = response[0]
            ask_price = response[1]

            orders = update_orders(last_bid_price, bid_price, last_ask_price, ask_price, orders)


            """original output:"""
            # quantity_bid = int(min(back_test.limit_percentage / 100 * back_test.balance,
            #                        back_test.limit_quantity, back_test.balance // cur_price))
            #
            # quantity_ask = int(min(back_test.limit_percentage / 100 * back_test.balance,
            #                        back_test.limit_quantity))
            #
            # back_test.check_order_ask(ask_price, quantity_ask)
            # back_test.check_order_bid(bid_price, quantity_bid)
            # last_bid_price = bid_price
            # last_ask_price = ask_price
            # back_test.all_orders_q += quantity_bid + quantity_ask


            if i < 40:
                quantity = int(min((back_test.limit_percentage * back_test.balance / cur_price) / 100,
                                   back_test.limit_quantity))
            else:
                quantity = model.calculate_quantity_1()

                r_h = back_test.global_q / back_test.all_orders_q

                model.update_rates_m_h(0, r_h)

            back_test.check_order_ask(ask_price, quantity)
            back_test.check_order_bid(bid_price, quantity)

            back_test.all_orders_q += 2 * quantity

            last_bid_price = bid_price
            last_ask_price = ask_price

            print("calc_quantity =   ", quantity)

        """OUTPUT"""

        print("CURRENCY       : " + str(back_test.balance))
        print("UNITS          : " + str(back_test.shares))
        print("CURRENT BALANCE: " + str(back_test.balance + back_test.shares * (last_bid_price + last_ask_price)/2))
        print("Q = " + str(back_test.global_q))


"""   Working with data and SQL   """

# all work with sql and data is collected in sql_work file

"""algorithm for real time trading"""


def algo_trade():

    BEST_MODEL_EVER_1 = model_1()
    BEST_MODEL_EVER_2 = model_2()

    working_figi = figi_usd

    try: old_LOB = get_LOB_data(working_figi)
    except:
        print("WARNING")
        print()

    time_c = 0

    print("start")

    for i in range(1000):

        try: LOB_data = get_LOB_data(working_figi)
        except:
            print("i am dead")
            print("Too many calls ERROR")
            time.sleep(2)
            time_c += 2
            print("loading...", time_c)
            continue

        if (old_LOB == None) or (old_LOB[0][0] == LOB_data[0][0] and old_LOB[0][1] == LOB_data[0][1]):
            time.sleep(0.6)
            time_c += 0.6
            print("loading...", time_c)

        else:
            time_c = 0
            print("///////////////////////////")

            print("quantity: ---", LOB_data[0][0], LOB_data[0][1])
            print("prices: -----", LOB_data[1][0], LOB_data[1][1])

            BEST_MODEL_EVER_1.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
            BEST_MODEL_EVER_1.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

            BEST_MODEL_EVER_2.update_LOB_data_b_a(LOB_data[0][0], LOB_data[0][1])
            BEST_MODEL_EVER_2.update_prices_b_a(LOB_data[1][0], LOB_data[1][1])

            response1 = BEST_MODEL_EVER_1.last_im_strategy()
            response2 = BEST_MODEL_EVER_1.last_im_v_strategy()
            response3 = BEST_MODEL_EVER_2.best_bid_ask()
            response4 = BEST_MODEL_EVER_2.last_and_along()


            #
            # quantity = BEST_MODEL_EVER_2.calulate_quantity_1()
            # print("Q, model_2 =   ", quantity)

            print("///////////////////////////")

            time.sleep(0.6)
            time_c += 0.6

        old_LOB = LOB_data


"""   Sample working   """


def main():

    # algo_trade()

    # acc_id_0 = create_new_account(100000, "usd")
    # sandbox_tester = SandboxTester(acc_id_0, token, figi_Tesla, "last_im_strategy", 100, 10, 10000)
    # # sandbox_tester = SandboxTester(acc_id_0, figi_usd, "last_im_v_strategy", 100, 10, 10000)
    # sandbox_tester.test()
    #
    # delete_account(acc_id_0)

    # ultimate_back_test(100000, 10000, "last_along_strategy")

    return 0

# strategies:  last_im_strategy  last_im_v_strategy  ask_bid_strategy  last_along_strategy


main()
