import csv
from collections import defaultdict

def foil_to_bool(foil_value):
    return foil_value.lower() == 'foil'

def read_csv(file_path):
    data = defaultdict(lambda: defaultdict(int))
    with open(file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = (row['Name'], row['Edition'], row['Edition code'], row["Collector's number"], str(foil_to_bool(row['Foil'])))
            data[key] = row
            data[key]['Quantity'] = int(row['Quantity'])
            data[key]['Foil'] = foil_to_bool(row['Foil'])
    return data

def compare_csv(old_file, new_file):
    old_data = read_csv(old_file)
    new_data = read_csv(new_file)

    differences = {}
    for key, new_row in new_data.items():
        if key not in old_data or new_row['Quantity'] > old_data[key]['Quantity']:
            differences[key] = new_row.copy()
            if key in old_data:
                differences[key]['Quantity'] = new_row['Quantity'] - old_data[key]['Quantity']

    return differences

def write_csv(file_path, data):
    if not data:
        print("No differences found.")
        return

    fieldnames = list(next(iter(data.values())).keys())
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data.values():
            row['Foil'] = str(row['Foil']).lower()  # Convert boolean to 'true' or 'false'
            writer.writerow(row)

if __name__ == "__main__":
    old_file = "Duskmourne_2024_Sep_22_08-36.csv"
    new_file = "Duskmourne_2024_Sep_25_09-03.csv"
    output_file = "new_items.csv"

    differences = compare_csv(old_file, new_file)
    write_csv(output_file, differences)
    print(f"New items have been written to {output_file}")