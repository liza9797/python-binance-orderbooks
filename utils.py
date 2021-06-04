import os
import requests
import argparse
import numpy as np


def get_arguments():
    parser = argparse.ArgumentParser(description='Script for downloading order books data from Binance exchange.')
    
    parser.add_argument('--symbol', '-s', type=str, default='BTCUSDT',
                        help='The Binance pair of coins.')
    parser.add_argument('--depth', type=int, default=5000,
                        help='The order books depth. Valid values: [5, 10, 20, 50, 100, 500, 1000, 5000]')
    parser.add_argument('--print-per-time', '-p', type=int, default=10,
                        help='The time period to print result.')
    parser.add_argument('--save-type', type=str, default="npy",
                        help='The datatype to use while saving.')
    parser.add_argument('--save-path', type=str, required=True, 
                        help='Path to save data.')
    return parser.parse_args()

def validate_args(args):
    
    assert args.depth in [5, 10, 20, 50, 100, 500, 1000, 5000]
    assert args.print_per_time > 0
    assert args.save_type in ["npy", "json", "csv"]
    if not os.path.exists(args.save_path):
        os.makedirs(args.save_path)

def make_request(url, result):
    res = requests.get(url).json()
    result.append(res)

def get_file_name(path, symbol, suffix, max_size, file_type=".npy"):
    files_list = os.listdir(path)
    files_list = [file[:-4] for file in files_list 
                          if (symbol in file) and (suffix in file) and (file_type in file)]
    files_num_list = [int(file.split("_")[-1]) for file in files_list]
    if len(files_num_list) > 0:
        max_num = np.max(files_num_list)
    else:
        max_num = 0
    
    file_path = os.path.join(path, symbol + "_" + suffix + "_{}{}".format(max_num, file_type))
    return file_path[:-4]
    
def update_file_name(file_path, max_size=500, file_type=".npy"):
    num = int(file_path.split("_")[-1])
    size = os.path.getsize(file_path + file_type)
    if (size / 1e6) < max_size:
        return file_path
    else:
        return "_".join(file_path.split("_")[:-1]) + "_{}".format(num + 1)
    
def to_csv_rows_format(data):
    if "asks" not in data.keys():
        print("NO ASKS,", data)
        rows_asks = []
    else:
        rows_asks = [",".join([data["loc_time"], "asks", pair[0], pair[1] ]) + "\n" for pair in data["asks"] 
                         if "asks" in data.keys()]
    
    if "bids" not in data.keys():
        print("NO BIDS,", data)
        rows_bids = []
    else:
        rows_bids = [",".join([data["loc_time"], "bids", pair[0], pair[1] ]) + "\n" for pair in data["bids"]
                         if "bids" in data.keys()]
    return rows_asks + rows_bids

def to_npy_rows_format(data):
    if "asks" not in data.keys():
        print("NO ASKS,", data)
        rows_asks = []
    else:
        
        prices = [pair[0] for pair in data["asks"]]
        min_price = np.min(np.array(prices).astype("float"))
        
        rows_asks = [data["loc_time"], min_price] + list(np.array(data["asks"]).astype("float").flatten() )
    
    if "bids" not in data.keys():
        print("NO BIDS,", data)
        rows_bids = []
    else:
        rows_bids = list(np.array(data["bids"]).astype("float").flatten() )
        
    return rows_asks + rows_bids