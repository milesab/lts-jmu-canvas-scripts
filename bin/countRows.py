import csv

with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\data\TRN FYR\FYR.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    row_count = sum(1 for row in reader)
    
print(f"Number of rows: {row_count}")