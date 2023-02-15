import csv

# Read the existing CSV file
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRraw.csv', 'r') as file:
    data = list(csv.reader(file))

# Create a list of new headers
new_headers = ['course_id', 'user_id', 'role', 'section_id', 'status']

# Add the new headers to the beginning of the list of lists
data.insert(0, new_headers)

# Write the updated data to a new CSV file
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRwithHeaders.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)