# importing pandas as pd
import pandas as pd

class CSVDataHandler:
    df = None
    def __init__(self):
        pass
        

    def create_df_from_list(self, names, values):
        self.names = names
        self.values = values
        # dictionary of lists
        dict = {}
        for i in range(len(self.names)):
            dict[self.names[i]] = self.values[i]
        df = pd.DataFrame(dict)
        self.df = df
        return df
    
    def print_df(self):
        print(self.df)

class JSONDataHandler:
    def __init__(self, names, values):
        self.names = names
        self.values = values
        self.create_json_from_list()

    def create_json_from_list(self):
        # dictionary of lists
        dict = {}
        for i in range(len(self.names)):
            dict[self.names[i]] = self.values[i]
        dict.json()

    def print_json(self):
        print(self.json).pretty()


    

# test  
if __name__ == "__main__":
    time = [0, 1, 2, 3]
    A0 = [90, 40, 80, 98]
    A1 = [90, 40, 80, 98]
    Relay_Val = [True, False, True, False]

    names = ['time_elapsed', 'A0', 'A1', 'Relay_Val']
    values = [time, A0, A1, Relay_Val]

    data_handler = CSVDataHandler()
    data_handler.create_df_from_list(names, values)
    data_handler.print_df()

