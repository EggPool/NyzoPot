"""
An object interfacing the Nyzo SqliteDB.
"""

import os
import sys
import sqlite3
from modules.sqlitebase import SqliteBase

TX_CHUNKS = 50  # How many tx at most per sql insert.

SQL_CREATE_DB = ["""CREATE TABLE blocks (
                    height                BIGINT    PRIMARY KEY ON CONFLICT FAIL,
                    previousBlockHash     BLOB (32),
                    startTimestamp        BIGINT,
                    verificationTimestamp BIGINT,
                    balanceListHash       BLOB (32),
                    verifierIdentifier    BLOB (32),
                    verifierSignature     BLOB (64),
                    hash                  BLOB (32) 
                    );""",
                 """CREATE UNIQUE INDEX idx_hash ON blocks (hash);""",
                 """CREATE TABLE transactions (
                    blockHeight        BIGINT,
                    id                 INTEGER,
                    type               INTEGER,
                    timestamp          BIGINT,
                    amount             INTEGER,
                    receiverIdentifier BLOB (32),
                    previousHashHeight BIGINT,
                    previousBlockHash  BLOB (32),
                    senderIdentifier   BLOB (32),
                    senderData         BLOB,
                    signature          BLOB (64) 
                );""",
                 """CREATE INDEX idx_height ON transactions (blockHeight);""",
                 """CREATE INDEX idx_id ON transactions (id);""",
                 """CREATE INDEX idx_type ON transactions (type);""",
                 """CREATE UNIQUE INDEX idx_signature ON transactions (signature);""",
                 """CREATE INDEX idx_receiver ON transactions (receiverIdentifier);""",
                 """CREATE INDEX idx_sender ON transactions (senderIdentifier);"""
                 ]


SQL_CLEAR = ['DELETE FROM blocks', 'DELETE FROM transactions']

SQL_INSERT_TRANSACTIONS_VALUES = "INSERT INTO transactions (blockHeight,id,type,timestamp,amount,receiverIdentifier," \
                                 "previousHashHeight,previousBlockHash,senderIdentifier,senderData,signature) VALUES "

SQL_INSERT_BLOCK = "INSERT INTO blocks (height, previousBlockHash, startTimestamp, verificationTimestamp, " \
                   "balanceListHash, verifierIdentifier, verifierSignature, hash) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"


class NyzoDB(SqliteBase):
    """
    Sqlite storage backend.
    """

    def __init__(self, verbose=False, db_path='./data/db', app_log=None, ram=False):
        self.verbose = verbose
        self.app_log = app_log
        SqliteBase.__init__(self, verbose=verbose, db_path=db_path, db_name='nyzo.db', app_log=app_log, ram=ram)

    # ========================= Generic DB Handling Methods ====================

    def check(self):
        """
        Checks and creates db. This is not async yet, so we close afterward.

        :return:
        """
        self.app_log.info("DB Check")
        if not os.path.isfile(self.db_path):
            res = -1
        else:
            # Test DB
            self.db = sqlite3.connect(self.db_path, timeout=1)
            self.db.text_factory = str
            self.cursor = self.db.cursor()
            # check if mempool needs recreating
            self.cursor.execute("PRAGMA table_info('blocks')")
            res = self.cursor.fetchall()
            # print(len(res), res)
            res = len(res)
        # No file or structure not matching
        if res != 8:
            try:
                self.db.close()
            except:
                pass
            try:
                pass
                # os.remove(self.db_path)
            except:
                pass
            self.db = sqlite3.connect(self.db_path, timeout=1)
            self.db.text_factory = str
            self.cursor = self.db.cursor()
            for sql in SQL_CREATE_DB:
                self.execute(sql)
            self.commit()
            self.app_log.info("Status: Recreated nyzo.db file")

        """self.db.close()
        self.db = None
        self.cursor = None
        """

    # ========================= Real useful Methods ====================

    async def clear(self):
        """
        Async. Empty db

        :return: None
        """
        for sql in SQL_CLEAR:
            await self.async_execute(sql, commit=True)
        # Good time to cleanup
        await self.async_execute("VACUUM", commit=True)

    def insert_transactions(self, transactions: list, block_height: int):
        offset = 0
        for chunk in self.chunks(transactions, TX_CHUNKS):
            values = [" (" + ", ".join([str(block_height), str(offset + id), str(tx.get_type()), str(tx.get_timestamp()),
                                        str(tx.get_amount()), f"X'{tx.get_receiver_identifier().hex()}'",
                                        str(tx._previous_hash_height), f"X'{tx._previous_block_hash.hex()}'",
                                        f"X'{tx.get_sender_identifier().hex()}'", f"X'{tx.get_sender_data().hex()}'",
                                        f"X'{tx.get_signature().hex()}'"
                                        ]) + ") "
                  for id, tx in enumerate(chunk)]
            offset += TX_CHUNKS
            if len(values):
                values = SQL_INSERT_TRANSACTIONS_VALUES + ",".join(values)
                # print(values)
                self.execute(values, commit=False)
        self.commit()

    def insert_block(self, block):
        self.execute(SQL_INSERT_BLOCK, (block._height, sqlite3.Binary(block._previous_block_hash),
                                        block._start_timestamp, block._verification_timestamp,
                                        sqlite3.Binary(block._balance_list_hash),
                                        sqlite3.Binary(block._verifier_identifier),
                                        sqlite3.Binary(block._verifier_signature),
                                        sqlite3.Binary(block.get_hash())
                                        ), commit=False)
        self.insert_transactions(block._transactions, block._height)

