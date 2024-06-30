import json

for year in range(2022, 2023):
    for month in range(1, 2):
        for day in range(2,3):
            print(f"year {year} month {month}")
            data = []
            error = []
            readfile = f"floorsheet/floorsheet-{year}-{month}-0{day}.txt"
            writefile = f"floorsheet/floorsheet-{year}-{month}-{day}.json"
            errorfile = f"floorsheet/floorsheet-error-{year}-{month}-{day}.json"
            try:
                with open(readfile,"r",encoding="ascii", errors='replace') as f:
                    for line in f:
                        try:
                            y = json.loads(line.strip())  # Parse the JSON string into a dictionary
                            y["no"] = int(y["no"])  # Convert "no" to an integer
                            y["buyer"] = int(y["buyer"])  # Convert "buyer" to an integer
                            y["seller"] = int(y["seller"])  # Convert "seller" to an integer
                            y["rate"] = float(y["rate"].replace(',', ''))  # Convert "rate" to a float after removing commas
                            y["quantity"] = int(y["quantity"].replace(',', ''))  # Convert "quantity" to an integer after removing commas
                            y["amount"] = float(y["amount"].replace(',', ''))  # Convert "amount" to a float after removing commas
                            data.append(y)  # Append the processed dictionary to the list
                        except json.JSONDecodeError as jde:
                            print(f"JSON decode error: {jde}")
                            print(line)
                            error.append(line)
                        except ValueError as ve:
                            print(f"Value error: {ve}")
                            print(line)
                            error.append(line)
                        except Exception as e:
                            print(f"Unexpected error: {e}")
                            print(line)
                            error.append(line)
            except FileNotFoundError as fnfe:
                print(f"File not found: {fnfe}")
                continue
            except Exception as e:
                print(f"Error opening file: {e}")
                continue

            try:
                with open(writefile, "w") as f:
                    for item in data:
                        f.write(json.dumps(item) + "\n")  # Convert dict to JSON string
            except Exception as e:
                print(f"Error writing to file: {e}")
            try:
                with open(errorfile, "w") as f:
                    for item in error:
                        f.write(str(error) + "\n")  # Convert dict to JSON string
            except Exception as e:
                print(f"Error writing to file: {e}")