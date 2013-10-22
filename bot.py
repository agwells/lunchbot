#!/usr/bin/env python

"""A really simple IRC bot."""

import sys
from twisted.internet import reactor, protocol
from twisted.words.protocols import irc

from smtplib import SMTP
from email.mime.text import MIMEText


orders = {}
menus = {
    'lbq': [
        # Two for One Tuesday Menu Pizzas.
        [ 'Margaret & Rita', 'Sliced roma tomato with fresh basil and even fresher buffalo mozzarella. V - $15.90' ],
        [ 'Good Ol\' Blue Bulls', 'Beef brisket braised in a beery BBQ sauce with roquette and bleu cheese. - $16.90' ],
        [ 'Do they Call Me Guiseppe the Pizza Maker?', 'Olives, capsicum, red onion, cherry tomatoes, artichoke hearts and feta. V - $15.90' ],
        [ 'Who Cut the Cheese?', 'Three cheese base with quadrants of bleu, brie, halloumi and gouda. V - $16.40' ],
        [ 'Le Coq', 'Citrus marinated chicken with balsamic roasted onion, brie and boozy plum sauce. - $16.70' ],
        [ 'Donald & Daisy go Asian', 'Duck with soy, orange, honey, hoisen and green peppercorn sauce with crunchy lettuce. - $18.10' ],
        [ 'Humungus Fungus', 'Porcini, gourmet brown and button mushroom sauce with shitake, oyster, portobello and enoki mushrooms. V - $16.90' ],
        [ 'Regresso Del Diablo', 'Spicy tomato sauce, chorizo, chilli flakes, chilli oil, jalapenos and capsicum. Choose your heat, house or fire dragon - $17.80' ],

        # Mains
        [ 'Pizza Bread', 'Sundried tomato pesto or garlic pizza bread. V  - $9.10' ],
        [ 'Falafel Burger', 'Falafel patty with oven-roasted tomato, red onion, lettuce, aubergine, artichokes and balsamic reduction on seeded bun with fries. VG, DF - $17.80' ],
        [ 'Summer Salad', 'Mixed leaf salad with artichoke hearts, cherry tomatoes, garlic and soy French beans, avocado and tapenade with falafel. GF, VG, DF. - $21.90' ],
        [ 'CousCous', 'Aubergine roasted with garlic, vine tomatoes, herbaceous couscous and red pepper coulis. DF,VG. - $21.20' ],
        [ 'El Pollo Loco Burger', 'Mango chicken with brie, tomato, lettuce, red onion, boozy plum sauce on seeded bun with fries and APAioli. - $19.60' ],
        [ 'Bacon CheeseBurger', 'Beef, beer and lamb patty, bacon, cheese, APAioli, tomato relish, onion jam, tomato, lettuce and onion with fries and APAioli. - $19.60' ]
    ],
    'lbqthurs' : [
        [ 'Chick Pea Salad', 'Warm salad of Carrot, Celery, Red cabbage, Kumara, Beetroot & pesto with Lemon dressing. V, GF. - $10, add Chorizo $5'],
        [ 'Caramelised Walnut Salad', 'Mixed lettuce leaves with Bleu cheese, Pear & Beetroot jam. V, GF. - $10, add Duck $6'],
        [ 'Chicken Skewers - Spicy', 'BBQ or basil pesto with house salad and youhurt dipping sauce. GF. - $10'],
        [ 'Chowder', 'Fresh mixed Seafood with Potatoes, Carrots, Onions & Celery. Served with Seeded Bread - $10'],
        [ 'Gnocchi', 'Kumara & Red Potato Gnocchi with Marinated feta, Spinach pesto & Toasted pine nuts. V. - $10'],
        [ 'Pork sandwich', 'Pulled Roasted pork with Jus on Ciabatta bread served with Fried Gourmet Potatoes tossed in Vinaigrette - $10'],
        [ 'Margherita Pizza', 'Basil pesto, Roma tomatoes & Mozzarella. V. - $10'],
        [ 'Chicken Pizza', 'Smoked Paprika roasted chicken with BBQ sauce & Haloumi - $10'],
    ],
    'lbqxmas': [
        [ 'ENTREE: soup', 'Tomato and fresh herb soup with fresh bread' ],
        [ 'ENTREE: pesto chicken', 'Grilled pesto chicken with feta, cucumber and tomato' ],
        [ 'ENTREE: garlic prawns', 'Garlic prawns with chilli, aioli and house salad' ],
        [ 'MAIN: courgette and cumin fritters', 'Courgette and cumin fritters with tomato chilli relish and radish, watercress and citrus fruit salad' ],
        [ 'MAIN: chicken roulade', 'Herb chicken roulade with grilled summer vegetables and roast red pepper coulis' ],
        [ 'MAIN: fish of the day', 'Pan-fried fish of the day with grilled summer vegetables and balsamic reduction' ],
        [ 'MAIN: steak', 'Stack with mushroom peppercorn sauch, house salad and kumara chips' ],
        [ 'DESSERT: beery ice cream', 'Wooden Spoon Freezery\'s beery ice cream with chocolate sauce' ],
        [ 'DESSERT: cheesecake', 'Baked dark chocolate and stout cheesecake with whipped cream' ],
        [ 'DESSERT: trifle', 'Summer fruit trifle of Victoria spounge, vanilla custard and sherry' ],
    ],
    'arizona': [
        [ 'Arizona Beef Burger', '200 gram grilled beef patty with bacon, cheese, mesclun, tomato, gherkins, barbeque chipotle sauce and roasted garlic mayo in a bug, served with chunky fries. $19.50' ],
        [ 'Chicken Burger', 'Grilled chicken breast with mesclun, tomato, avacado and roasted garlic mayo in a bin, served with chunky fries. $20'],
    ],
}

emails = {
    'lbq': [
        'Little Beer Quarter <littlebeerquarter@xtra.co.nz>',
        'Hugh Davenport <hugh@davenport.net.nz>',
        'Haydn Newport <haydn@catalyst.net.nz>',
    ],
    'lbqxmas': [
        'Little Beer Quarter <littlebeerquarter@xtra.co.nz>',
        'Hugh Davenport <hugh@davenport.net.nz>',
        'Haydn Newport <haydn@catalyst.net.nz>',
    ],
    'arizona': [
        'Arizona <cu@arizona.co.nz>',
        'Hugh Davenport <hugh@davenport.net.nz>',
        'Haydn Newport <haydn@catalyst.net.nz>',
    ],
}

fromemail = 'Lunchbot (Haydn Newport) <haydn@catalyst.net.nz>'
toemail = None

menu = None

protocols = []

disabled_commands = []#'help', 'menu', 'info', 'order', 'cancel', 'list', 'open', 'close']
ignore_nick = []
admin_nick = [ 'aquaman',
               'aquaghost',
               'aqualaptop',
               'superspring',
               'heiko',
               'haddock',
               'wi11',
               'haydn',
               'haydnn',
             ]
admin_commands = [ 'send',
                   'open',
                   'close',
                 ]

def maybe_int(x):
    try: return int(x)
    except: return -1   # bs

class Bot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    _sentQueue = []
    users = {}

    def signedOn(self):
        self.join(self.factory.channel)
        self.channel = self.factory.channel
        protocols.append(self)
        self.lineRate = 0.0
        print "Signed on as %s." % self.nickname

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        protocols.remove(self)

    def joined(self, channel):
        print "Joined %s." % channel

    def act(self, user, channel, cmd):
        username = user.split('!',1)[0]
        if channel == self.nickname:
            channel = username
        global orders, menu, disabled_commands, toemail, ignore_nick, admin_nick, admin_commands
        if username in ignore_nick:
            return
        parts = cmd.split(' ',2)
        op = parts[0]
        if op in disabled_commands:
            return
        if op in admin_commands and not username in admin_nick:
            self.msg(channel, 'sorry you are not an admin')
            return
        if op == 'help':
            self.msg(channel, '- !help: show this message.')
            self.msg(channel, '- !menu: show the menu.')
            self.msg(channel, '- !info <n>: show info for an item on the menu.')
            self.msg(channel, '- !order [<nick>] <n> <special instructions>: order your lunch. `no beetroot` etc can go in `special instructions`')
            self.msg(channel, '- !cancel: cancel your order')
            self.msg(channel, '- !list: list current lunch orders')
            self.msg(channel, '- !msg <message>: Show a message on all channels')
            self.msg(channel, '- !notordered: Show a list of users that have not ordered')
            if username in admin_nick:
              self.msg(channel, '- !open <menu>: open orders for today, clear state')
              self.msg(channel, '- !send: Send a mailing of the order to the restaurant')
              self.msg(channel, '- !close: close orders')
        if op == 'order':
            if not menu:
                self.msg(channel, 'orders are not open.')
                return

            if len(parts) < 2:
                self.msg(channel, 'i\'m confused about what you wanted.')
                return

            item = maybe_int(parts[1])
            if item == -1 and len(parts) > 2:
                parts = cmd.split(' ',3)
                username = parts.pop(1)
                item = maybe_int(parts[1])
            if item < 0 or item >= len(menu):
                self.msg(channel, 'that\'s not a thing.')
                return

            special = len(parts) > 2 and parts[2] or None

            if not username in orders:
                orders[username] = []

            orders[username].append((item,special))
            if special:
                msgAll('%s added a %s, with instructions: %s.' % \
                    (username, menu[item][0], special))
            else:
                msgAll('%s added a %s.' % (username, menu[item][0]))

        if op == 'menu':
            if not menu:
                self.msg(channel, 'orders are not open.')
                return

            self.msg(channel, 'menu:')
            for i,m in enumerate(menu):
                self.msg(channel, '%d) %s' % (i,m[0]))
            self.msg(channel, '-- end of menu --');

        if op == 'info':
            if not menu:
                self.msg(channel, 'orders are not open.')
                return

            if len(parts) < 2:
                self.msg(channel, 'i\'m confused about what you wanted info on.')

            item = maybe_int(parts[1])
            if item < 0 or item >= len(menu):
                self.msg(channel, 'that\s not a thing.')
                return

            self.msg(channel, '%d) %s - %s' % (item, menu[item][0], menu[item][1]))

        if op == 'cancel':
            if not menu:
                self.msg(channel, 'orders are not open.')
                return

            if len(parts) > 1:
                parts = cmd.split(' ',2)
                username = parts.pop(1)
            if username not in orders:
                self.msg(channel, 'you don\'t have anything ordered!')
            else:
                del orders[username]
                msgAll('%s cancelled their order.' % username)

        if op == 'list':
            if not menu:
                self.msg(channel, 'orders are not open.')
                return

            self.msg(channel, '%d orders for today:' \
                % sum(len(v) for _,v in orders.items()))
            by_type = pivot_to_values(flatten_values(orders))
            for o,n in sorted(by_type.items(), key=lambda x:len(x[1])):
                instr = o[1] and '(%s) ' % (o[1],) or ''
                self.msg(channel, '%dx %s %s[%s]' % \
                    (len(n), menu[o[0]][0], instr, ','.join(n)))
            self.msg(channel, '-- end of orders --');

        if op == 'open':
            if len(parts) < 2:
                self.msg(channel, 'you didn\'t specify a menu. valid menus are:');
                for mn in menus.keys():
                    self.msg(channel, '* %s' % (mn,))
                return
            if parts[1] not in menus:
                self.msg(channel, '%s is not a known menu.' % (parts[1],))
            menu = menus[parts[1]]
            toemail = emails[parts[1]]
            orders = {}
            msgAll('orders are now open for %s!' % (parts[1],))

        if op == 'close':
            msgAll('orders are now closed.');
            orders = {}
            menu = None
            toemail = None

        if op == 'msg':
            if len(parts) < 2:
                self.msg(channel, 'you didn\'t specify what you want to message');
                return
            msgAll('<%s> %s' % (username, ' '.join(parts[1:])));

        if op == 'notordered':
            if not menu:
                self.msg(channel, 'orders are not open')
                return

            self.msg(channel, 'The following have not ordered anything: %s' % (', '.join(map(str, list(set(self.users[channel]) - set(orders.keys()))))))

        if op == 'send':
            if not menu:
                self.msg(channel, 'orders are not open')
                return

            if len(orders) == 0:
                self.msg(channel, 'nothing has been ordered!')
                return

            global fromemail

            if len(parts) > 1:
                time = parts[1:]
            else:
                time = 'today 12:15pm'
            body = 'Hi, would we be able to make a booking for %s\n' % time
            body += '%d orders for today:' \
                % (sum(len(v) for _,v in orders.items()))
            by_type = pivot_to_values(flatten_values(orders))
            for o,n in sorted(by_type.items(), key=lambda x:len(x[1])):
                instr = o[1] and '(%s) ' % (o[1],) or ''
                body += '\n%dx %s %s[%s]' % \
                    (len(n), menu[o[0]][0], instr, ','.join(n))
            body += '\n\nThanks, can we please get a reply to confirm this order?\n\n'
            body += 'Cheers, Haydn\n021 032 8216';

            self.msg(channel, body)

            msg = MIMEText(body)
            msg['Subject'] = 'Order for %s' % time
            msg['From'] = fromemail
            msg['To'] = ', '.join(map(str, toemail))

            s = SMTP('localhost')
            s.sendmail(fromemail, toemail, msg.as_string())
            s.quit()

            msgAll('orders have been sent to %s.' % toemail)

        if op == 'isadmin':
            if len(parts) < 2:
                self.msg(channel, 'yes, you are an admin' if username in admin_nick else 'no, you are not an admin')
                return
            self.msg(channel, 'yes, %s is an admin' % (parts[1]) if parts[1] in admin_nick else 'no, %s is not an admin' % (parts[1]))

        if op == 'thank' or op == 'thanks':
            if len(parts) < 2:
                self.msg(channel, 'No problem %s' % (username) )
                return
            self.msg(channel, 'Thanks %s! :)' % (parts[1]))


    def privmsg(self, user, channel, msg):
        print 'channel: `%s` user: `%s` msg: `%s`' % (user, channel, msg)
        if msg.startswith('!'):
            self.act( user, channel, msg[1:] )
        elif msg.startswith('lunchbot: '):
            self.act( user, channel, msg[10:] )

    def irc_NOTICE(self, prefix, params):
        if params[1] == '*** Message to %s throttled due to flooding' % (self.factory.channel):
            self.lineRate += 0.1
            self._queue.insert(0, self._sentQueue.pop())
            if not self._queueEmptying:
                self._sendLine()
            print "Flooding detected, lineRate now at %0.1f seconds" % self.lineRate

    def irc_RPL_NAMREPLY(self, prefix, params):
        self.users[params[2]] = params[3].split(' ')
        self.users[params[2]].remove(self.nickname)

    def userJoined(self, user, channel):
        if user != self.nickname:
            self.users[channel].append(user)

    def userLeft(self, user, channel):
        self.users[channel].remove(user)

    def userKicked(self, user, channel, kicker, message):
        self.users[channel].remove(user)

    def userRenamed(self, olduser, newuser):
        # TODO: change orders as well
        for l in self.users:
            try:
                self.users[l].remove(olduser)
                self.users[l].append(newuser)
            except:
                pass

    def userQuit(self, user, reason):
        for l in self.users:
            try:
                l.remove(user)
            except:
                pass

    def _reallySendLine(self, line):
        if line.startswith('PRIVMSG '):
            self._sentQueue.append(line)
            if len(self._sentQueue) > 20:   # This value is arbitary that "feels like a sensible limit"
                self._sentQueue.pop()
        return irc.IRCClient._reallySendLine(self, line)

    def lineReceived(self, line):
        #print line
        irc.IRCClient.lineReceived(self, line)

def flatten_values(xs):
    for k,x in xs.items():
        for x_ in x: yield (k,x_)

def pivot_to_values(xs):
    result = {}
    for k,v in xs:
        if v not in result: result[v] = [k]
        else: result[v].append(k)
    return result

def msgAll(msg):
    for protocol in protocols:
        protocol.msg(protocol.channel, msg)

class BotFactory(protocol.ClientFactory):
    protocol = Bot

    def __init__(self, channel, nickname='lunchbot'):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Connection lost. Reason: %s" % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Connection failed. Reason: %s" % reason

if __name__ == "__main__":
    reactor.connectTCP('irc.wgtn.cat-it.co.nz', 6667, BotFactory('#lunch'))
    reactor.connectTCP('irc.freenode.org', 6667, BotFactory('##catalystlunch'))
    reactor.run()
