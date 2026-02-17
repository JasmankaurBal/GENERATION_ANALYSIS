import pandas as pd

def read_file(upload_file):
    filename=upload_file.filename.lower()

    if filename.endswith("xlsx") or filename.endwith(".xls"):
        return pd.read_excel(upload_file.file)
    
    elif filename.endswith("csv"):
        return pd.read_csv(upload_file.file)
    
    else:
        raise Exception("Unsupported file format")
    
    df.columns=df.columns.str.strip().str.lower()

    return df
    

    