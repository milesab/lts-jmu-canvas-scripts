import csv

# Read the existing CSV file
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRformatted.csv', 'r') as file:
    data = list(csv.reader(file))

# Add static values to columns
for row in data:
    row[0] = 'Transfer_Enrollment_Modules_Fall_2023'  # static value for 'course_id'
    row[2] = 'student'   # static value for 'role'
    row[4] = 'active'    # static value for 'status'

# Write the updated data to a new CSV file
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRcomplete.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)