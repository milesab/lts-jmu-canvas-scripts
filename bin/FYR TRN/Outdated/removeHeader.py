import csv

inputFromSA = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\data\TRN FYR\FYR.csv'
headersRemoved = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRraw.csv'


with open(input_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # skip the first row (header row)
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for row in reader:
            writer.writerow(row)  # write the row to the output file
