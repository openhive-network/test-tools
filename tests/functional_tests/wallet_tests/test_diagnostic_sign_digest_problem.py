from __future__ import annotations
import concurrent.futures
from datetime import datetime
import time

import pytest
import test_tools as tt
from beekeepy import PackedBeekeeper
import concurrent

def sign_func(wallet_name: str, limit, bk: PackedBeekeeper):
    beeekeeper = bk.unpack()
    key = "STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4"
    digest = "9b29ba0710af3918e81d7b935556d7ab205d8a8f5ca2e2427535980c2e8bdaff"

    with beeekeeper.create_session() as session:
        wallet = session.open_wallet(wallet_name)
        wallet.unlock("password")
        for _ in range(limit):
            # time_before = datetime.now()
        
            wallet.sign_digest(sig_digest=digest, key=key)
            # tt.logger.info(f"Czas podpisu: {datetime.now() - time_before}")

# def test_diagnostic_sec():
#     wallet = tt.Wallet()
#     wallet.api.import_key("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n")
#     dupa = wallet.api.list_keys()
#     for _ in range(100):
#         sign_func(wallet=wallet)


# def test_diagnostic_thr():
#     total = 1000
#     limit_max_workers = 1
#     wallet = tt.Wallet()
#     wallet.api.import_key("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n")
#     dupa = wallet.api.list_keys()

#     time_before = datetime.now()
#     with concurrent.futures.ThreadPoolExecutor(max_workers=limit_max_workers) as exe:
#         for _ in range(limit_max_workers):
#             exe.submit(sign_func, wallet, int(total/limit_max_workers))
#     tt.logger.info(f"Czas podpisu: {datetime.now() - time_before}")



def test_diagnostic_thr2():
    total = 50000
    limit_max_workers = 10
    wallet = tt.Wallet()
    wallet.api.import_key("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n")
    dupa = wallet.api.list_keys()
    beekeeper_binary = wallet.beekeeper_binary.pack()
    with concurrent.futures.ProcessPoolExecutor(max_workers=limit_max_workers) as exe:
        futures: list[concurrent.futures.Future] = []
        for _ in range(limit_max_workers):
            futures.append(exe.submit(sign_func, wallet.name, int(total/limit_max_workers), beekeeper_binary))

        start = time.perf_counter()
        while (
            len((tasks := concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED))[0])
            > 0
        ):
            futures.pop(futures.index(tasks[0].pop()))
            tt.logger.debug(f"Joined next item after {(time.perf_counter() - start) :.4f} seconds...")
            start = time.perf_counter()
