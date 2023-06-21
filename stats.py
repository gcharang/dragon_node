#!/usr/bin/env python3
import time
import os
import const
import helper
import datetime
from daemon import DaemonRPC
from logger import logger
from color import ColorMsg

class StatsLine:
    def __init__(self, column_widths, coin="KMD"):
        # Todo: last mined KMD since
        self.msg = ColorMsg()
        self.coin = coin
        self.col_widths = column_widths
        self.daemon = DaemonRPC(self.coin)   
        
    def last_block_time(self):
        best_block = self.daemon.rpc.getbestblockhash()
        best_blk_info = self.daemon.rpc.getblock(best_block)
        last_block = best_blk_info["time"]
        return last_block

    def ntx_utxo_count(self, utxo_value):
        utxo_value = helper.get_utxo_value(self.coin)
        unspent = self.daemon.listunspent()
        count = 0
        for utxo in unspent:
            if utxo["amount"] == utxo_value:
                count += 1
        return count

    def connections(self):
        networkinfo = self.daemon.getnetworkinfo()
        return networkinfo["connections"]

    def wallet_size(self):
        filename = helper.get_wallet_path(self.coin)
        filesize = os.path.getsize(filename)
        if filesize > 10485760:
            return '\033[31m' + "   > 10M" + '\033[0m' 
        elif filesize > 5242880:
            return '\033[33m' + f"    > 5M" + '\033[0m' 
        elif filesize < 1048576:
            return '\033[33m' + f"    > 1M" + '\033[0m' 
        else:
            return helper.bytes_to_unit(filesize)

    def get(self) -> list:
        if self.coin == "KMD_3P":
            row = ["KMD (3P)"]
        elif self.coin in const.COINS_3P:
            row = [f"{self.coin} (3P)"]
        else:
            row = [self.coin]
        try:
            # Notarizations        
            wallet_tx = self.daemon.listtransactions()
            ntx_stats = helper.get_ntx_stats(wallet_tx, self.coin)
            ntx_count = ntx_stats[0]
            row.append(str(ntx_count))
            
            last_ntx_time = ntx_stats[1]
            if last_ntx_time == 0:
                dhms_since = '\033[31m' + "   Never" + '\033[0m' 
            else:
                sec_since = helper.sec_since(last_ntx_time)
                dhms_since = helper.sec_to_dhms(sec_since)
            row.append(dhms_since)
            
            last_mined = ntx_stats[2]

            ntx_utxo_count = self.ntx_utxo_count(self.coin)
            if ntx_utxo_count < 5:
                ntx_utxo_count = '\033[31m' + f"     {ntx_utxo_count}" + '\033[0m'
            elif ntx_utxo_count < 10:
                ntx_utxo_count = '\033[33m' + f"     {ntx_utxo_count}" + '\033[0m'
            elif ntx_utxo_count > 100:
                ntx_utxo_count = '\033[31m' + "> 100" + '\033[0m'
            elif ntx_utxo_count > 40:
                ntx_utxo_count = '\033[92m' + f"    {ntx_utxo_count}" + '\033[0m'
            elif ntx_utxo_count >= 10:
                ntx_utxo_count = '\033[92m' + f"    {ntx_utxo_count}" + '\033[0m'
            row.append(str(ntx_utxo_count))

            balance = self.daemon.getbalance()
            if balance < 0.1:
                row.append('\033[31m' + f"     {balance:.3f}" + '\033[0m')
            else:
                row.append(f"{balance:.3f}")

            # Blocks
            block_count = self.daemon.getblockcount()
            row.append(str(block_count))
            last_blocktime = self.daemon.last_block_time(block_count)
            if last_blocktime == 0:
                dhms_since = '\033[31m' + "   Never" + '\033[0m' 
            else:
                sec_since = helper.sec_since(last_blocktime)
                dhms_since = helper.sec_to_dhms(sec_since, True, 600, 1800, 7200)
            row.append(str(dhms_since))

            connections = self.connections()
            row.append(str(connections))
            
            wallet_size = self.wallet_size()
            row.append(str(wallet_size))
            
            tx_count = len(wallet_tx)
            row.append(str(tx_count))
            
            start = time.perf_counter()
            r = self.daemon.rpc("listunspent")
            response_time = time.perf_counter() - start
            row.append(f"{response_time:.4f}")

        except Exception as e:
            return [f"Error getting stats for {self.coin}. Is it running?"]
        return row


class Stats:
    def __init__(self, coins: list) -> None:
        self.coins = coins
        self.coins.sort()
        self.msg = ColorMsg()
        self.col_widths = [12, 6, 8, 6, 10, 10, 8, 6, 8, 8, 8]
        self.columns = [
            "COIN", "NTX", "LASTNTX", "UTXO", "BALANCE",
            "BLOCKS", "LASTBLK", "CONN", "SIZE", "NUMTX", "TIME"
        ]
        self.table_width = sum(self.col_widths) + 2 * (len(self.col_widths) + 1)
        
    def format_line(self, row: list) -> str:
        line = " | "
        for i in range(len(row)):
            if i in [0]:
                line += f"{str(row[i]).ljust(self.col_widths[i])} |"
            else:
                line += f"{str(row[i]).rjust(self.col_widths[i])} |"
        return line
    
    def header(self) -> str:
        return self.format_line(self.columns)
    
    def spacer(self) -> str:
        return " " + "-" * self.table_width
    
    def format_errors(self, errors: str) -> str:
        return "| " + errors.center(self.table_width - 4) + " |"
    
    def show(self) -> None:
        print()
        print(self.header())
        print(self.spacer())
        for coin in self.coins:
            line = StatsLine(self.col_widths, coin)
            row = line.get()
            if len(row) == 1:
                errors = self.format_errors(row[0])
                print(self.msg.colorize(errors, "lightred"))
            else:
                print(self.format_line(row))
        print(self.spacer())
        date_str = '| ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' |'
        fmt_date_str = str(date_str).rjust(self.table_width + 1)
        print(fmt_date_str)
