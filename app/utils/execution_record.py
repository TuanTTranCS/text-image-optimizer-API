import csv
import os
from datetime import datetime

def execution_time_record(db_record:dict):
    """
    Record execution time to csv file, taken db_record dictionary as input

    """

    recorded_parameters = ['created_timestamp', 'user',
                         'api_source', 'model',
                         'execution_time_ms',
                         'prompt_tokens_count', 'completion_tokens_count',
                         'finish_reason']
    
    task = db_record['task']
    csv_file = f'./test_init/{task}_records.csv'

    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(recorded_parameters)

    else:
        data_to_write = {k:v for k,v in db_record.items() if k in recorded_parameters}
        with open(csv_file, mode='a', newline='') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames = recorded_parameters) 
            writer.writerow(data_to_write) 
    return