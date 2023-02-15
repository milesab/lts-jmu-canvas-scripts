from pathlib import Path
import csv, time

start_time = time.time()

currentPath = Path(__file__).parent
input_file = 'Data\FYR.csv'
inputFromSA = (currentPath / input_file).resolve()

print(inputFromSA)

##inputFromSA = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYR.csv'
formattedFYR = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRformatted.csv'
finalFYR = r'C:\Users\milesab\Documents\GitHub\lts-jmu-canvas-scripts\bin\FYR TRN\Data\FYRcomplete.csv'

# Read the FYR file supplied by SA
with open(inputFromSA, 'r') as file:
    data = list(csv.DictReader(file))


# Create a new list of dictionaries (new_data) with the user_id column assigned
new_data = []
for row in data:
    user_id = row.pop('user_id')
    row['user_id'] = user_id
    new_data.append(row)


# Write the data to a csv named FYRformatted that properly labels the headers
with open(formattedFYR, 'w', newline='') as file:
    headers = ['course_id', 'user_id', 'role', 'section_id', 'status']
    writer = csv.DictWriter(file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(new_data)

# Read FYRFormatted
with open(formattedFYR, 'r') as file:
    formattedData = list(csv.reader(file))
    
# Add static values to columns
for row in formattedData:
    row[0] = 'Transfer_Enrollment_Modules_Fall_2023'  # static value for 'course_id'
    row[2] = 'student'   # static value for 'role'
    row[4] = 'active'    # static value for 'status'
    
# Write static values to FYRcomplete, ready to be uploaded
with open(finalFYR, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(formattedData)
    
print("--- %s seconds ---" % (time.time() - start_time))