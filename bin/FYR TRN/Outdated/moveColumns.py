import csv

inputFromSA = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYR.csv'

# Read the FYR file supplied by SA
with open(inputFromSA, 'r') as file:
    data = list(csv.DictReader(file))


# Create a new list of dictionaries (new_data) with the user_id column assigned
new_data = []
for row in data:
    user_id = row.pop('user_id')
    row['user_id'] = user_id
    new_data.append(row)


# Write the updated data to a new CSV file FYRFormatted
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRformatted.csv', 'w', newline='') as file:
    headers = ['course_id', 'user_id', 'role', 'section_id', 'status']
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(new_data)

# Read FYRFormatted
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRformatted.csv', 'r') as file:
    formattedData = list(csv.reader(file))
    print(formattedData)
    
# Add static values to columns
for row in formattedData:
    row[0] = 'Transfer_Enrollment_Modules_Fall_2023'  # static value for 'course_id'
    row[2] = 'student'   # static value for 'role'
    row[4] = 'active'    # static value for 'status'
    
# Write values to a new csv
with open(r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRcomplete.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(formattedData)