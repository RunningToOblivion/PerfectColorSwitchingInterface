import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import numpy as np

class ColorReplacerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Replacer")

        # Instruction label
        self.instruction_label = tk.Label(root, text="Click on the image to select the color to replace.")
        self.instruction_label.pack()

        # Set up UI components
        self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.pick_color_from_image)

        self.open_button = tk.Button(root, text="Open Image", command=self.open_image)
        self.open_button.pack()

        self.new_color_button = tk.Button(root, text="Select New Color", command=self.select_new_color)
        self.new_color_button.pack()

        self.tolerance_label = tk.Label(root, text="Tolerance:")
        self.tolerance_label.pack()
        
        self.tolerance_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
        self.tolerance_slider.pack()

        self.apply_button = tk.Button(root, text="Apply Color Change", command=self.apply_color_change)
        self.apply_button.pack()

        self.cancel_button = tk.Button(root, text="Cancel Changes", command=self.cancel_changes)
        self.cancel_button.pack()

        self.save_button = tk.Button(root, text="Save Image", command=self.save_image)
        self.save_button.pack()

        # Initialize variables
        self.image = None
        self.original_image = None
        self.tk_image = None
        self.selected_color = None
        self.new_color = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = Image.open(file_path).convert("RGBA")
            self.original_image = self.image.copy()
            self.display_image(self.image)

    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image.resize((500, 500)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def pick_color_from_image(self, event):
        if not self.image:
            return
        x = int(event.x * self.image.width / 500)
        y = int(event.y * self.image.height / 500)
        self.selected_color = self.image.getpixel((x, y))[:3]
        messagebox.showinfo("Selected Color", f"Color to replace: {self.selected_color}")

    def select_new_color(self):
        color = colorchooser.askcolor()[0]
        if color:
            self.new_color = tuple(map(int, color))
            messagebox.showinfo("New Color", f"New color: {self.new_color}")

    def apply_color_change(self):
        if not self.image or self.selected_color is None or self.new_color is None:
            messagebox.showerror("Error", "Please load an image, select a color from the image, and choose a new color.")
            return

        tolerance = self.tolerance_slider.get()
        image_data = np.array(self.image)

        target_color = np.array(self.selected_color, dtype=np.float32)
        new_color = np.array(self.new_color, dtype=np.float32)

        # Calculate brightness of target and new colors
        target_brightness = np.mean(target_color)
        new_color_brightness = np.mean(new_color)

        # Calculate the Euclidean distance for each pixel's color to the selected color
        distances = np.sqrt(np.sum((image_data[:, :, :3].astype(np.float32) - target_color) ** 2, axis=-1))

        # Create a mask for pixels within the tolerance
        mask = distances <= tolerance

        # Apply color change with brightness adjustment
        for y in range(image_data.shape[0]):
            for x in range(image_data.shape[1]):
                if mask[y, x]:
                    # Calculate the pixel's brightness relative to the target color
                    pixel_brightness = np.mean(image_data[y, x, :3].astype(np.float32))
                    brightness_factor = pixel_brightness / target_brightness if target_brightness != 0 else 1.0
                    
                    # Adjust the new color's brightness
                    adjusted_color = np.clip(new_color * brightness_factor, 0, 255).astype(np.uint8)
                    
                    # Apply the adjusted color to the pixel
                    image_data[y, x, :3] = adjusted_color

        # Update and display the modified image
        self.image = Image.fromarray(image_data)
        self.display_image(self.image)

    def cancel_changes(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.display_image(self.image)

    def save_image(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Image Saved", f"Image saved as {file_path}")
        else:
            messagebox.showerror("Error", "No image to save. Please load and modify an image first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorReplacerApp(root)
    root.mainloop()
