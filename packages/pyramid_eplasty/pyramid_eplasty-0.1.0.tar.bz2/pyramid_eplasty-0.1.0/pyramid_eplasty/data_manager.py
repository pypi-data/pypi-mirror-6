from eplasty.session import Session

class EPDataManager():
    
    def __init__(self, pool, connection ):
        self.connection = connection
        self.session = Session(self.connection)
        self.pool = pool

    def abort(self, transaction):
        pass

    def tpc_begin(self, transaction):
        pass

    def tpc_vote(self, transaction):
        pass

    def commit(self, transaction):
        self.session.flush()

    def tpc_finish(self, transaction):
        self.connection.commit()
        self.connection.close()
        self.pool.putconn(self.connection)

    def tpc_abort(self, transaction):
        self.session.rollback()
        self.connection.close()
        self.pool.putconn(self.connection)
