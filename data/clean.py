import csv

def filter_csv_with_synopsis(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Filter out rows with empty synopsis
        filtered_rows = [row for row in reader if row['synopsis'].strip()]

        # Write the filtered rows to a new CSV file
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_csv:
            writer = csv.DictWriter(output_csv, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in filtered_rows:
                writer.writerow(row)

input_file = "all_books.csv"
output_file = "books.csv"

filter_csv_with_synopsis(input_file, output_file)
print(f"Rows without 'synopsis' have been removed and saved to {output_file}")