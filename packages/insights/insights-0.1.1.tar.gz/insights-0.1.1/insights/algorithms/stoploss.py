#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from intuition.zipline.algorithm import TradingFactory
import insights.plugins.database as database


# https://www.quantopian.com/posts/auto-adjusting-stop-loss
class AutoAdjustingStopLoss(TradingFactory):
    def initialize(self, properties):
        if properties.get('save', 0):
            self.use(database.RethinkdbBackend(self.identity, True)
                     .save_portfolio)

        self.base_price = properties.get('base_price', 10)

        self.stock = {}

    def event(self, data):
        signals = {}
        scale = {}

        for sid in data:
            current_price = data[sid].price
            r_o_r = 0

            #Check if this stock is already in portfolio
            if sid in self.portfolio.positions.keys():
                # Check if the sell price needs to be updated
                purchase_price = self.portfolio.positions[sid].cost_basis
                if purchase_price > 0:
                    r_o_r = (current_price - purchase_price) / purchase_price
                    sell_price = (1 - ((-r_o_r * .05) + .10)) * current_price

                    if r_o_r > 1.5:
                        if (.9 * r_o_r) > data[sid]:
                            data[sid] = (.9 * r_o_r)

                    elif r_o_r > 1:
                        if (1.8 * purchase_price) > data[sid]:
                            data[sid] = 1.8 * purchase_price
                        signals[sid] = current_price
                        scale[sid] = 1
                        #self.order(sid, self.base_price)
                        message = "Bought 10 shares of %s sold for return \
                            of %.2f" % (sid, r_o_r)
                        self.logger.info(message)

                    elif r_o_r > .5:
                        if (1.35 * purchase_price) > self.stock[sid]:
                            self.stock[sid] = 1.35 * purchase_price
                        #self.order(sid, 2 * self.base_price)
                        signals[sid] = current_price
                        scale[sid] = 2
                        message = "Bought 20 shares of %s sold for return \
                            of %.2f" % (sid, r_o_r)
                        self.logger.info(message)

                    elif r_o_r > .15:
                        if (1.05 * purchase_price) > self.stock[sid]:
                            self.stock[sid] = 1.05 * purchase_price
                        #self.order(sid, 3 * self.base_price)
                        signals[sid] = current_price
                        scale[sid] = 3
                        message = "Bought 30 shares of %s sold for return \
                            of %.2f" % (sid, r_o_r)
                        self.logger.info(message)

                    elif r_o_r > .05:
                        if (.95 * purchase_price) > self.stock[sid]:
                            self.stock[sid] = .95 * purchase_price
                        #self.order(sid, 4 * self.base_price)
                        signals[sid] = current_price
                        scale[sid] = 4
                        message = "Bought 40 shares of %s sold for return \
                            of %.2f" % (sid, r_o_r)
                        self.logger.info(message)

                    current_shares = self.portfolio.positions[sid].amount
                    if self.stock[sid] > current_price:
                        #self.order(sid, -current_shares)
                        signals[sid] = -current_price
                        scale[sid] = 1
                        message = "Sold %d shares of %s sold for return \
                            of %.2f" % (current_shares, sid, r_o_r)
                        self.logger.info(message)
            else:
                #self.order(sid, self.base_price)
                signals[sid] = current_price
                scale[sid] = 1
                message = "Bought 10 shares of %s bought at %s" \
                    % (sid, current_price)
                self.logger.info(message)
                sell_price = .85 * current_price
                self.stock[sid] = sell_price

        self.manager.advise(scale=scale)
        return signals
