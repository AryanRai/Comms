# importing pandas as pd
import pandas as pd
import os

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

    def df_to_csv(self, path):
        self.df.to_csv(path)
    
    def df_to_json(self):
        return self.df.to_json(orient='records')

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

class FolderHandler:
    #create folder if it doesnt exist
    def create_folder(self, path):
        os.makedirs(path, exist_ok=True)
        return True
    
    def check_folder(self, path):
        return os.path.exists(path)

    def list_subfolders(self, path):
        return [f.name for f in os.scandir(path) if f.is_dir()]
    

# test  
if __name__ == "__main__":
    fol = FolderHandler()
    print(fol.list_subfolders("Modules/"))

