import csv
import json

class ExportService:
    def __init__(self, data):
        self.data = data

    def export_to_csv(self, file_path):
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.data[0].keys())  # write header
            for row in self.data:
                writer.writerow(row.values())  # write data

    def export_to_json(self, file_path):
        with open(file_path, mode='w') as file:
            json.dump(self.data, file, indent=4)