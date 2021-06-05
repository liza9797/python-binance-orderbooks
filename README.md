# Python Binance OrderBooks

The python script for downloading order books using [Binance API](https://binance-docs.github.io/apidocs/spot/en/#order-book) in real time. The main properties of the solution:
- The frequency of requests is automatically choosen in accordance with the selected depth and API limits.
- Waiting for a response from the exchange - no more than 5 seconds. If the waiting time is exceeded, the next request is made.
- The data is written to the file until the file size does not exceed 1000 MB, then the next file is created.

## Usage 

   ```sh
   python save_order_books.py --symbol=COIN-PAIR-FROM-BINANCE --depth=ORDER-BOOKS-DEPTH 
                              --save-type=DATA-TYPE-TO-USE --save-path=PATH-TO-SAVE
   ```

