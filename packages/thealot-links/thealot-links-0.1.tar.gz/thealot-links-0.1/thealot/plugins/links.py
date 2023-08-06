from .plugin import Plugin
from sqlalchemy.sql.expression import func
from sqlalchemy import Column, Integer, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    key = Column(Text, primary_key=True)
    url = Column(Text, nullable=False)

    def __str__(self):
        return '[{}]({})'.format(self.key, self.url)


class LinksPlugin(Plugin):

    help = {
            }

    def hook(self):
        Base.metadata.create_all(self.bot.db.get_bind())
        self.bot.commands['link'] = self.command

    def unhook(self):
        if 'link' in self.bot.help:
            del self.bot.help['link']
        if 'link' in self.bot.commands:
            del self.bot.commands['link']

    def get_link(self, key):
        result = self.bot.db.query(Link).get(key)
        if result is not None:
            print(type(result))
            return result.url
        else:
            return "Link not found" #404

    def add(self, key, url):
        try:
            self.bot.db.add(Link(key=key, url=url))
            self.bot.db.commit()
            return "Link added"
        except Exception as e:
            self.bot.db.rollback()
            return "Link already exists"

    def command(self, source, target, arguments=None):
        if target == self.bot.config['nickname']:
            target = source
        message = ""

        if arguments:
            if arguments[:3] == "add":
                try:
                    key, url = arguments[3:].split(maxsplit=1)
                    message = self.add(key, url)
                except ValueError:
                    message = "Expecting two arguments"

            else:
                message = self.get_link(arguments)

        if message:
            self.message(target, message)
