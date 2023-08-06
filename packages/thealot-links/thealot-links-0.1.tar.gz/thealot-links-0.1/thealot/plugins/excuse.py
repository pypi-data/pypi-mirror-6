from .plugin import Plugin
from sqlalchemy.sql.expression import func
from sqlalchemy import Column, Integer, Text, Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Excuse(Base):
    __tablename__ = 'excuse'

    LEADIN = 'L'
    PERPETRATOR = 'P'
    FACTOR = 'F'

    id = Column(Integer, primary_key=True)
    string_type = Column(Enum(LEADIN, PERPETRATOR, FACTOR, name="string_type"))
    string = Column(Text, nullable=False)

    def __str__(self):
        return self.string


"""
Inspired by http://www.mandatory.com/2013/05/06/the-ultimate-excuse-creator/
"""
class ExcusePlugin(Plugin):

    help = {
        "excuse": "random excuse",
            }

    def hook(self):
        if Excuse.__tablename__ not in self.bot.db.get_bind().table_names():
            Base.metadata.create_all(self.bot.db.get_bind())
            types = (Excuse.LEADIN, Excuse.PERPETRATOR, Excuse.FACTOR)
            strings = (LEADINS, PERPETRATORS, FACTORS)
            for (t, strings) in zip(types, strings):
                for s in strings:
                    self.bot.db.add(Excuse(string_type=t, string=s))
            self.bot.db.commit()
        self.bot.commands['excuse'] = self.excuse

    def unhook(self):
        if 'excuse' in self.bot.help:
            del self.bot.help['excuse']
        if 'excuse' in self.bot.commands:
            del self.bot.commands['excuse']

    def excuse(self, source, target, arguments=None):
        if target == self.bot.config['nickname']:
            target = source

        print(target)

        leadin = self.bot.db.query(Excuse).filter_by(string_type=Excuse.LEADIN).order_by(func.random()).first()
        perpetrator = self.bot.db.query(Excuse).filter_by(string_type=Excuse.PERPETRATOR).order_by(func.random()).first()
        factor = self.bot.db.query(Excuse).filter_by(string_type=Excuse.FACTOR).order_by(func.random()).first()

        excuse = '{} {} {}.'.format(leadin, perpetrator, factor)

        self.message(target, excuse)

    def random_element(self, items):
        return items[random.randrange(len(items))]
