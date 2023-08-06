from .plugin import Plugin
import sqlalchemy.ext
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from random import choice

Base = declarative_base()


class Quote(Base):
    __tablename__ = 'quote'

    id = Column(Integer, primary_key=True)
    quote = Column(Text, nullable=False)


class QuotePlugin(Plugin):
    help = {
        "quote": "random quote",
        "quote <text>": "random quote containing <text>",
        "quote add <text>": "quote add <text> to quotes",
        "quote delete <number>": "delete quote with id <number>",
    }

    def hook(self):
        Base.metadata.create_all(self.bot.db.get_bind())
        self.bot.commands['quote'] = self.command

    def unhook(self):
        if 'quote' in self.bot.help:
            del self.bot.help['quote']
        if 'quote' in self.bot.commands:
            del self.bot.commands['quote']

    def command(self, source, target, arguments=None):
        if target == self.bot.config['nickname']:
            target = source

        if arguments:
            if arguments[:3] == "add":
                self.notice(source, self.add(arguments[3:]))
            elif arguments[:6] == "delete":
                self.notice(source, self.delete(arguments[6:]))
            else:
                self.message(target, self.quote(arguments))
        else:
            self.message(target, self.quote())

    def add(self, quote):
        if quote:
            q = Quote(quote=quote)
            try:
                self.bot.db.add(q)
                self.bot.db.commit()
                return "Quote added as %d." % (q.id,)
            except sqlalchemy.exc:
                self.bot.db.rollback()
                return "Failed to add the quote."
        else:
            return "Nothing to add."

    def delete(self, uid):
        if id:
            try:
                quote = self.bot.db.query(Quote).get(uid)
                self.bot.db.delete(quote)
                self.bot.db.commit()
                return "Quote deleted."
            except sqlalchemy.orm.exc.UnmappedInstanceError:
                return "Failed to delete."
        else:
            return "Specify quote ID to delete."

    def quote(self, search=""):
        try:
            quote = choice(self.bot.db.query(Quote).filter(Quote.quote.contains(search)).all())
            return "{}| {}".format(quote.id, quote.quote)
        except IndexError:
            return "Quote not found"
