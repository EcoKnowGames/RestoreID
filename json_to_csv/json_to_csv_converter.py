import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

def json_to_csv(json_files, output_path):
    fieldnames = [
        'participation_code', 'level_id', 'start_treasury', 'no_rounds', 
        'user_id', 'timestamp', 'readable_timestamp', 'start_approval',
        'country', 'round_number', 'action_number', 'population', 
        'round_start_treasury', 'current_treasury', 'action',
        'cost', 'x_loc', 'y_loc'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both array and object meta formats
                if isinstance(data['meta'], list):
                    meta = data['meta'][0]
                else:
                    meta = data['meta']
                
                participation_code = meta.get('participation_code', '')
                level_id = meta.get('level_id', '')
                
                # Handle numeric fields with better error checking
                try:
                    start_treasury = int(meta.get('startTreasury', 0))
                    no_rounds = int(meta.get('noOfRounds', 0))
                    timestamp = int(meta.get('timestamp', 0))
                    start_approval = int(meta.get('startApproval', 0))
                except (ValueError, TypeError) as e:
                    messagebox.showerror("Numeric Conversion Error",
                        f"Error converting numeric values in {file}:\n{str(e)}")
                    continue
                
                readable_timestamp = datetime.fromtimestamp(timestamp).isoformat()
                country = meta.get('country', '')
                user_id = meta.get('user_id', '')
                
                for round_data in data['round']:
                    round_number = round_data.get('roundNumber', 0)
                    population = round_data.get('population', 0)
                    treasury = round_data.get('treasury', 0)
                    current_treasury = treasury
                    turns = round_data.get('turn', [])
                    
                    if not turns:
                        writer.writerow({
                            'participation_code': participation_code,
                            'level_id': level_id,
                            'start_treasury': start_treasury,
                            'no_rounds': no_rounds,
                            'user_id': user_id,
                            'timestamp': timestamp,
                            'readable_timestamp': readable_timestamp,
                            'start_approval': start_approval,
                            'country': country,
                            'round_number': round_number,
                            'action_number': 0,
                            'population': population,
                            'round_start_treasury': treasury,
                            'current_treasury': treasury,
                            'action': 'PASS',
                            'cost': 0,
                            'x_loc': -1,
                            'y_loc': -1
                        })
                    else:
                        for j, turn in enumerate(turns):
                            try:
                                cost = int(turn.get('cost', 0))
                                action = turn.get('action', '')
                                
                                if action == 'CHOP':
                                    cost = -1 * cost
                                current_treasury -= cost
                                
                                loc = turn.get('loc', {'x': -1, 'y': -1})
                                x_loc = loc.get('x', -1)
                                y_loc = loc.get('y', -1)
                                
                                writer.writerow({
                                    'participation_code': participation_code,
                                    'level_id': level_id,
                                    'start_treasury': start_treasury,
                                    'no_rounds': no_rounds,
                                    'user_id': user_id,
                                    'timestamp': timestamp,
                                    'readable_timestamp': readable_timestamp,
                                    'start_approval': start_approval,
                                    'country': country,
                                    'round_number': round_number,
                                    'action_number': j,
                                    'population': population,
                                    'round_start_treasury': treasury,
                                    'current_treasury': current_treasury,
                                    'action': action,
                                    'cost': cost,
                                    'x_loc': x_loc,
                                    'y_loc': y_loc
                                })
                            except Exception as e:
                                messagebox.showerror("Turn Processing Error",
                                    f"Error processing turn {j} in round {round_number} of {file}:\n{str(e)}")
                                continue
            except Exception as e:
                messagebox.showerror("File Processing Error",
                    f"Unexpected error processing file {file}:\n{str(e)}")
                continue

class JSONToCSVConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON to CSV Converter")
        
        self.json_files = []
        
        # UI Elements
        self.select_btn = tk.Button(root, text="Select JSON Files", command=self.select_files)
        self.select_btn.pack(pady=10)
        
        self.output_label = tk.Label(root, text="Output CSV File:")
        self.output_label.pack()
        
        self.output_entry = tk.Entry(root, width=50)
        self.output_entry.pack(pady=5)
        
        self.browse_btn = tk.Button(root, text="Browse...", command=self.browse_output)
        self.browse_btn.pack(pady=5)
        
        self.convert_btn = tk.Button(root, text="Convert to CSV", command=self.convert)
        self.convert_btn.pack(pady=10)
        
        self.status_label = tk.Label(root, text="Select JSON files and output location")
        self.status_label.pack(pady=10)
    
    def select_files(self):
        self.json_files = filedialog.askopenfilenames(
            title="Select JSON Files",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if self.json_files:
            self.status_label.config(text=f"Selected {len(self.json_files)} files")
    
    def browse_output(self):
        output_file = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if output_file:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_file)
    
    def convert(self):
        if not self.json_files:
            messagebox.showerror("Error", "Please select JSON files first")
            return
        
        output_path = self.output_entry.get()
        if not output_path:
            messagebox.showerror("Error", "Please select output file")
            return
        
        if not output_path.endswith('.csv'):
            output_path += '.csv'
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_path)
        
        self.status_label.config(text="Converting...")
        self.root.update()
        
        try:
            json_to_csv(self.json_files, output_path)
            messagebox.showinfo("Success", f"Conversion complete!\nSaved to {output_path}")
            self.status_label.config(text="Conversion complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Conversion failed:\n{str(e)}")
            self.status_label.config(text="Conversion failed")

if __name__ == "__main__":
    root = tk.Tk()
    app = JSONToCSVConverter(root)
    root.mainloop()