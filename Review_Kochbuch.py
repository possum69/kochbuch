import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
try:
    from PIL import Image, ImageTk
except ImportError:
    import tkinter.messagebox as messagebox
    messagebox.showerror("Error", "Could not load PIL (Pillow) library. Images will not be displayed.")
    Image = None
    ImageTk = None

IMAGE_PATH = "Bilder"

class RecipeBook:
    image_index = 0
    def __init__(self, root):
        self.root = root
        self.root.title("Kochbuch")
        self.root.geometry("1200x800")
        
        # Load recipe data
        self.load_recipes()
        
        # Create main layout
        self.create_layout()
        
        # Initial recipe display
        if self.recipes:
            self.display_recipe(self.recipes[0])

    def load_recipes(self):
        try:
            with open('Kochbuch.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.recipes = data['documents']
                self.total_recipes = data['total']
        except Exception as e:
            messagebox.showerror("Error", f"Could not load recipe book: {e}")
            self.recipes = []
            self.total_recipes = 0

    def create_layout(self):
        # Create left panel for recipe list
        left_panel = ttk.Frame(self.root, padding="5")
        left_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Search box
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_recipes)
        search_entry = ttk.Entry(left_panel, textvariable=self.search_var)
        search_entry.pack(fill=tk.X, pady=(0, 5))

        # Recipe list
        self.recipe_list = ttk.Treeview(left_panel, columns=("name",), show="tree")
        self.recipe_list.heading("#0", text="")
        self.recipe_list.column("#0", width=0, stretch=tk.NO)
        self.recipe_list.pack(fill=tk.BOTH, expand=True)
        self.recipe_list.bind('<<TreeviewSelect>>', self.on_select_recipe)

        # Populate recipe list
        self.populate_recipe_list()

        # Create middle panel for recipe details
        middle_panel = ttk.Frame(self.root, padding="10")
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create right panel for image
        right_panel = ttk.Frame(self.root, padding="10")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Recipe detail widgets
        self.name_var = tk.StringVar()
        ttk.Label(middle_panel, text="Name:").pack(anchor=tk.W)
        self.name_entry = ttk.Entry(middle_panel, textvariable=self.name_var, width=50)
        self.name_entry.pack(fill=tk.X)

        self.chapter_var = tk.StringVar()
        ttk.Label(middle_panel, text="Kapitel:").pack(anchor=tk.W)
        self.chapter_entry = ttk.Entry(middle_panel, textvariable=self.chapter_var, width=50)
        self.chapter_entry.pack(fill=tk.X)

        self.serves_var = tk.StringVar()
        ttk.Label(middle_panel, text="Portionen:").pack(anchor=tk.W)
        self.serves_entry = ttk.Entry(middle_panel, textvariable=self.serves_var, width=10)
        self.serves_entry.pack(anchor=tk.W)

        self.duration_var = tk.StringVar()
        ttk.Label(middle_panel, text="Dauer (Minuten):").pack(anchor=tk.W)
        self.duration_entry = ttk.Entry(middle_panel, textvariable=self.duration_var, width=10)
        self.duration_entry.pack(anchor=tk.W)

        # Ingredients
        ttk.Label(middle_panel, text="Zutaten:").pack(anchor=tk.W)
        self.ingredients_text = tk.Text(middle_panel, height=10, width=50)
        self.ingredients_text.pack(fill=tk.X)

        # Instructions
        ttk.Label(middle_panel, text="Anleitung:").pack(anchor=tk.W)
        self.instructions_text = tk.Text(middle_panel, height=10, width=50)
        self.instructions_text.pack(fill=tk.X)

        # Notes
        ttk.Label(middle_panel, text="Notizen:").pack(anchor=tk.W)
        self.notes_text = tk.Text(middle_panel, height=3, width=50)
        self.notes_text.pack(fill=tk.X)

        # Image display
        self.image_label = ttk.Label(right_panel)
        self.image_label.pack(pady=10)

        # Button frame for save and delete buttons
        button_frame = ttk.Frame(middle_panel)
        button_frame.pack(pady=10)
        
        # Add button
        add_button = ttk.Button(button_frame, text="Neu", command=self.add_recipe)
        add_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_button = ttk.Button(button_frame, text="Speichern", command=self.save_recipe)
        save_button.pack(side=tk.LEFT, padx=5)

        # Rotate image button
        rotate_button = ttk.Button(button_frame, text="Nächstes Bild", command=self.display_image)
        rotate_button.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        delete_button = ttk.Button(button_frame, text="Löschen", command=self.delete_recipe, style="Delete.TButton")
        delete_button.pack(side=tk.LEFT, padx=5)
        
        # Delete image button
        image_delete_button = ttk.Button(button_frame, text="Bilder löschen", command=self.delete_image, style="Delete.TButton")
        image_delete_button.pack(side=tk.LEFT, padx=5)

        # Add image button
        add_image_button = ttk.Button(button_frame, text="Bild hinzufügen", command=self.add_image)
        add_image_button.pack(side=tk.LEFT, padx=5)
        
        # Create a style for the delete button
        style = ttk.Style()
        style.configure("Delete.TButton", foreground="red")

    def populate_recipe_list(self, filter_text=""):
        self.recipe_list.delete(*self.recipe_list.get_children())
        for recipe in self.recipes:
            if filter_text.lower() in recipe['Name'].lower():
                self.recipe_list.insert("", "end", values=(recipe['Name'],))

    def filter_recipes(self, *args):
        self.populate_recipe_list(self.search_var.get())

    def on_select_recipe(self, event):
        selection = self.recipe_list.selection()
        if selection:
            recipe_name = self.recipe_list.item(selection[0])['values'][0]
            recipe = next((r for r in self.recipes if r['Name'] == recipe_name), None)
            if recipe:
                self.display_recipe(recipe)

    def display_recipe(self, recipe):
        self.recipe = recipe
        # Clear previous content
        self.name_var.set(recipe.get('Name', ''))
        self.chapter_var.set(recipe.get('Kapitel', ''))
        self.serves_var.set(str(recipe.get('Serves', '')))
        self.duration_var.set(str(recipe.get('Dauer', '')))
        
        # Clear and set ingredients
        self.ingredients_text.delete('1.0', tk.END)
        if 'Zutaten' in recipe:
            self.ingredients_text.insert('1.0', '\n'.join(recipe['Zutaten']))

        # Clear and set instructions
        self.instructions_text.delete('1.0', tk.END)
        if 'Anleitung' in recipe:
            self.instructions_text.insert('1.0', '\n'.join(recipe['Anleitung']))

        # Clear and set notes
        self.notes_text.delete('1.0', tk.END)
        if 'Notes' in recipe and recipe['Notes']:
            self.notes_text.insert('1.0', recipe['Notes'])

        # Display image if available
        self.display_image(index=0)

    def display_image(self, index=None):
        image_names = self.recipe.get('Bild')
        if image_names and len(image_names) > 0 and Image and ImageTk:
            if not index:
                index = self.image_index
                index = (index + 1) % len(image_names)
            image_name = image_names[index]  # Display the first image for now
            self.image_index = index
            try:
                # Look for image in Input directory
                image_path = os.path.join(IMAGE_PATH, image_name)
                if os.path.exists(image_path):
                    image = Image.open(image_path)
                    # Resize image to fit the window while maintaining aspect ratio
                    max_size = (800, 1400)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo  # Keep a reference
                else:
                    self.image_label.configure(image='')
                    if image_name:
                        self.image_label.configure(text=f"Image not found: {image_path}")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.image_label.configure(image='', text=f"Error loading image: {image_name}")
        else:
            self.image_label.configure(image='', text="No images available" if image_names else "")

    def delete_recipe(self):
        selection = self.recipe_list.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Rezept zum Löschen aus.")
            return
        
        recipe_name = self.recipe_list.item(selection[0])['values'][0]
        if messagebox.askyesno("Löschen bestätigen", 
                             f"Möchten Sie das Rezept '{recipe_name}' wirklich löschen?"):
            recipe_index = next((i for i, r in enumerate(self.recipes) 
                               if r['Name'] == recipe_name), None)
            
            if recipe_index is not None:
                # Remove the recipe
                deleted_recipe = self.recipes.pop(recipe_index)
                self.total_recipes -= 1
                
                # Save changes to file
                try:
                    with open('Kochbuch.json', 'w', encoding='utf-8') as f:
                        json.dump({'total': self.total_recipes, 'documents': self.recipes}, 
                                f, ensure_ascii=False, indent=4)
                    
                    # Remove image file if it exists
                    if deleted_recipe.get('Bild'):
                        image_path = os.path.join('Input', deleted_recipe['Bild'])
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except Exception as e:
                                print(f"Could not delete image file: {e}")
                    
                    messagebox.showinfo("Erfolg", "Rezept wurde erfolgreich gelöscht!")
                    
                    # Refresh the recipe list
                    self.populate_recipe_list(self.search_var.get())
                    
                    # Clear the detail view
                    self.clear_recipe_details()
                except Exception as e:
                    messagebox.showerror("Error", f"Fehler beim Löschen des Rezepts: {e}")

    def clear_recipe_details(self):
        self.name_var.set('')
        self.chapter_var.set('')
        self.serves_var.set('')
        self.duration_var.set('')
        self.ingredients_text.delete('1.0', tk.END)
        self.instructions_text.delete('1.0', tk.END)
        self.notes_text.delete('1.0', tk.END)
        self.image_label.configure(image='', text='')

    def delete_image(self):
        selection = self.recipe_list.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Rezept zum Speichern aus.")
            return

        recipe_name = self.recipe_list.item(selection[0])['values'][0]
        recipe_index = next((i for i, r in enumerate(self.recipes) if r['Name'] == recipe_name), None)
        
        if recipe_index is not None:
            # Update recipe data
            self.recipes[recipe_index].update({
                'Bild': []
            })

            # Save to file
            try:
                with open('Kochbuch.json', 'w', encoding='utf-8') as f:
                    json.dump({'total': self.total_recipes, 'documents': self.recipes}, 
                            f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Recipe saved successfully!")
                
                # Refresh the recipe list
                self.populate_recipe_list(self.search_var.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not save recipe: {e}")

    def save_recipe(self):
        selection = self.recipe_list.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Rezept zum Speichern aus.")
            return

        recipe_name = self.recipe_list.item(selection[0])['values'][0]
        recipe_index = next((i for i, r in enumerate(self.recipes) if r['Name'] == recipe_name), None)
        
        if recipe_index is not None:
            # Update recipe data
            self.recipes[recipe_index].update({
                'Name': self.name_var.get(),
                'Kapitel': self.chapter_var.get(),
                'Serves': int(self.serves_var.get()) if self.serves_var.get().isdigit() else 1,
                'Dauer': int(self.duration_var.get()) if self.duration_var.get().isdigit() else 0,
                'Zutaten': self.ingredients_text.get('1.0', tk.END).strip().split('\n'),
                'Anleitung': self.instructions_text.get('1.0', tk.END).strip().split('\n'),
                'Notes': self.notes_text.get('1.0', tk.END).strip()
            })

            # Save to file
            try:
                with open('Kochbuch.json', 'w', encoding='utf-8') as f:
                    json.dump({'total': self.total_recipes, 'documents': self.recipes}, 
                            f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Recipe saved successfully!")
                
                # Refresh the recipe list
                self.populate_recipe_list(self.search_var.get())
            except Exception as e:
                messagebox.showerror("Error", f"Could not save recipe: {e}")

    def add_recipe(self):
        recipe_name = self.name_var.get()
        self.recipes.append({
            'Name': self.name_var.get(),
            'Kapitel': self.chapter_var.get(),
            'Serves': int(self.serves_var.get()) if self.serves_var.get().isdigit() else 1,
            'Dauer': int(self.duration_var.get()) if self.duration_var.get().isdigit() else 60,
            'Zutaten': self.ingredients_text.get('1.0', tk.END).strip().split('\n'),
            'Anleitung': self.instructions_text.get('1.0', tk.END).strip().split('\n'),
            'Notes': self.notes_text.get('1.0', tk.END).strip()
        })

        # Save to file
        try:
            with open('Kochbuch.json', 'w', encoding='utf-8') as f:
                json.dump({'total': len(self.recipes), 'documents': self.recipes}, 
                        f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Success", "Recipe saved successfully!")
            
            # Refresh the recipe list
            self.populate_recipe_list(self.search_var.get())
        except Exception as e:
            messagebox.showerror("Error", f"Could not save recipe: {e}")                

    def add_image(self):
        selection = self.recipe_list.selection()
        if not selection:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Rezept zum Speichern aus.")
            return

        recipe_name = self.recipe_list.item(selection[0])['values'][0]
        recipe_index = next((i for i, r in enumerate(self.recipes) if r['Name'] == recipe_name), None)
        
        if recipe_index is not None:
            # Open file dialog to select image
            file_path = filedialog.askopenfilename(title="Bild auswählen", 
                                                   filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
            if file_path:
                image_name = os.path.basename(file_path)
                dest_path = os.path.join(IMAGE_PATH, image_name)
                
                # Copy image to Bilder directory
                try:
                    os.makedirs(IMAGE_PATH, exist_ok=True)
                    if file_path != dest_path:
                        with open(file_path, 'rb') as src_file:
                            with open(dest_path, 'wb') as dest_file:
                                dest_file.write(src_file.read())
                except Exception as e:
                    pass
                    #messagebox.showerror("Error", f"Could not add image: {e}")

                # Update recipe data
                current_images = self.recipes[recipe_index].get('Bild', [])
                current_images.append(image_name)
                self.recipes[recipe_index]['Bild'] = current_images

                # Save to file
                with open('Kochbuch.json', 'w', encoding='utf-8') as f:
                    json.dump({'total': self.total_recipes, 'documents': self.recipes}, 
                            f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Success", "Image added successfully!")
                
                # Refresh the recipe list
                self.populate_recipe_list(self.search_var.get())
                    
if __name__ == "__main__":
    root = tk.Tk()
    app = RecipeBook(root)
    root.mainloop()