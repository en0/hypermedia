from config import ConfigBase
class ProductionConfig(ConfigBase):

    ## Database Connection Schema for SQL ALCHEMY
    DATABASE_URI = 'mysql://user@host:password/schema'

