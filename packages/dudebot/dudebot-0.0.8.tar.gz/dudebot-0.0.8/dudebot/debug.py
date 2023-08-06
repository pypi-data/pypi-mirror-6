import sys
from dudebot import core


class SimulatedChatRoom(core.Connector):

    def __init__(self, nickname, other_users):
        super(SimulatedChatRoom, self).__init__()
        self.nickname = nickname
        self.users = [nickname]
        self.users.extend(other_users)
        if len(self.users) < 2:
            raise NeedMoreUsers(u"Add users to the current_user key")
        self.current_user = self.users[1]

    def join_chatroom(self, chatroom):
        pass

    def run_forever(self):
        print u"People in chatroom: {0}".format(self.users)
        print u"/changeto nickname <- Changes to given nickname"
        print u"Otherwise, just type to chat"
        print u"(Hit enter after each line!)"

        while True:
            try:
                prompt = u"%s> " % self.current_user
                text = raw_input(prompt)
                self.handle_message(self.current_user, text)
            except EOFError:
                sys.exit(-1)

    def output(self, text):
        print text

    def handle_message(self, sender, text):
        if text.startswith(u"/changeto "):
            new_user = text.split()[1]

            if new_user in self.users:
                self.current_user = new_user
            else:
                self.output(u"Nothing known about " +new_user)
        else:
            for ai in self.botais:
                response = ai.respond(sender, text)
                if response is not None:
                    response_text = u"%s> %s" % (self.nickname,response)
                    self.output(response_text)


class NeedMoreUsers(Exception):
    pass
