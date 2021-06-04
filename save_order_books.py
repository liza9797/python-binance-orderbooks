import os
import time
import json
import requests
import numpy as np
import multiprocessing
from npy_append_array import NpyAppendArray

from utils import *

depth_to_weight = {
    5: 1, 10: 1, 20: 1, 50: 1, 100: 1,
    500: 5, 
    1000: 10,
    5000: 50
}
    
    
if __name__ == "__main__":
    args = get_arguments()
    validate_args(args)
    
    ### Get time
    timer = time.time()

    ### Parameters
    wait_time = 60 / (1200 / depth_to_weight[args.depth])
    path = args.save_path
    suffix = "order_books_{}_depth".format(args.depth)
    
    ### Data storages
    DATA = []
    ROWS = []
    
    ### File path and npy-file
    FILE_PATH = get_file_name(path, args.symbol, suffix, max_size=1000)
    ROWS_NPY = NpyAppendArray(FILE_PATH + ".npy")

    iter_start = time.time()

    while 1: ### Endless cycle

        try:

            ### If the time gone is more than print_per_time, 
            ### it saves data and free storages
            if time.time() - timer > args.print_per_time:
                
                ### Prints
                print("--- saving data ({:.2f} sec) ---".format(time.time() - timer))
                print("\t\t{}: {} items".format(args.symbol, len(DATA)))
                
                ### Update time
                timer = time.time()

                ### Save data
                if args.save_type == "json":
                    with open(FILE_PATH + ".json", "a") as f:
                        json.dump(DATA, f)
                elif args.save_type == "csv":
                    with open(FILE_PATH + ".csv", "a") as f:
                        f.write("".join(ROWS)  )
                
                ### Update file path and data storages
                FILE_PATH = update_file_name(FILE_PATH, file_type=".npy")
                ROWS_NPY = NpyAppendArray(FILE_PATH + ".npy")
                DATA = []
                ROWS = []

            ### If the time from the last request is less than wait_time,
            ### it is required to waid due to Binance limitations
            if time.time() - iter_start < wait_time:
                time.sleep(wait_time - time.time() + iter_start + 0.1)
            iter_start = time.time()

            ### Make request
            result = []
            url = "https://api.binance.com/api/v3/depth?symbol={}&limit={}".format(args.symbol, args.depth)
            p = multiprocessing.Process(target=make_request(url, result))
            p.start()

            ### Wait for 5 seconds or until process finishes
            p.join(5)

            ### If thread is still active, kill it
            if p.is_alive():
                print("running... let's kill it...")
                p.terminate()
                p.kill()
                p.join()
            res = result[0]

            ### Store for json
            res["loc_time"] = str(time.time())
            DATA.append(res)

            ### Store for csv
            rows = to_csv_rows_format(res)
            ROWS += rows

            ### Store for npy
            rows = to_npy_rows_format(res)
            array = np.array(rows).astype(float)
            if  args.save_type == "npy":
                ROWS_NPY.append(array.reshape((1, array.shape[0])) )

        except Exception as e:
            print(e)
