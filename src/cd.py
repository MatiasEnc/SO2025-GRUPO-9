import os 

def cd(path_to):
    try:
        os.chdir(path_to)
    except Exception as e:
       print(e) 

