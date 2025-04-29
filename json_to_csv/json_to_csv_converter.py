import json
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class JSONToCSVConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the main window
        
        self.json_files = []
        self.output_path = ""
        
        # Start the sequential process
        self.select_files()
        self.root.mainloop()  # This is the correct placement for mainloop

    def select_files(self):
        """Step 1: Select JSON files"""
        self.json_files = filedialog.askopenfilenames(
            title="Step 1/3 - Select JSON Files to Convert",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        
        if not self.json_files:
            messagebox.showinfo("Cancelled", "File selection was cancelled.")
            self.root.quit()
            return
        
        self.select_output_location()

    def select_output_location(self):
        """Step 2: Select output CSV location"""
        output_file = filedialog.asksaveasfilename(
            title="Step 2/3 - Select Output CSV Location",
            defaultextension=".csv",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*")),
            initialfile="converted_data.csv"
        )
        
        if not output_file:
            messagebox.showinfo("Cancelled", "Output selection was cancelled.")
            self.root.quit()
            return
        
        self.output_path = output_file
        self.confirm_conversion()

    def confirm_conversion(self):
        """Step 3: Confirm before conversion"""
        response = messagebox.askyesno(
            "Step 3/3 - Confirm Conversion",
            f"Convert {len(self.json_files)} JSON file(s) to CSV?\n\n"
            f"Output will be saved to:\n{self.output_path}",
            icon='question'
        )
        
        if response:
            self.convert_files()
        else:
            messagebox.showinfo("Cancelled", "Conversion was cancelled.")
            self.root.quit()

    def convert_files(self):
        """Perform the actual conversion"""
        try:
            fieldnames = [
                'participation_code', 'level_id', 'start_treasury', 'no_rounds', 
                'user_id', 'timestamp', 'readable_timestamp', 'start_approval',
                'country', 'round_number', 'action_number', 'population', 
                'round_start_treasury', 'current_treasury', 'action',
                'cost', 'x_loc', 'y_loc'
            ]
            
            with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for file in self.json_files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Handle both array and object meta formats
                        meta = data['meta'][0] if isinstance(data['meta'], list) else data['meta']
                        
                        # Extract meta data with defaults
                        participation_code = meta.get('participation_code', '')
                        level_id = meta.get('level_id', '')
                        start_treasury = int(meta.get('startTreasury', 0))
                        no_rounds = int(meta.get('noOfRounds', 0))
                        user_id = meta.get('user_id', '')
                        timestamp = int(meta.get('timestamp', 0))
                        readable_timestamp = datetime.fromtimestamp(timestamp).isoformat()
                        start_approval = int(meta.get('startApproval', 0))
                        country = meta.get('country', '')
                        
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
                        messagebox.showerror(
                            "File Error",
                            f"Error processing file {file}:\n{str(e)}",
                            parent=self.root
                        )
                        continue
            
            # Show completion message
            messagebox.showinfo(
                "Conversion Complete",
                f"Successfully converted {len(self.json_files)} file(s) to:\n{self.output_path}",
                parent=self.root
            )
            
        except Exception as e:
            messagebox.showerror(
                "Conversion Error",
                f"An error occurred during conversion:\n{str(e)}",
                parent=self.root
            )
        
        self.root.quit()

if __name__ == "__main__":
    JSONToCSVConverter()