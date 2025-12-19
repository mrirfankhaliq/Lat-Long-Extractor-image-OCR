import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pytesseract
import re
import os
import sys
from datetime import datetime
from pathlib import Path
import threading

def check_tesseract_in_path():
    """Check if tesseract is available in system PATH"""
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

# Try to set Tesseract path for Windows if not in PATH
if sys.platform == 'win32':
    # Get current script/executable directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        script_dir = os.path.dirname(sys.executable)
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_paths = [
        # Check local folder first (same directory as exe)
        os.path.join(script_dir, 'tesseract-ocr', 'tesseract.exe'),
        os.path.join(script_dir, 'tesseract-ocr', 'bin', 'tesseract.exe'),
        os.path.join(script_dir, 'Tesseract-OCR', 'tesseract.exe'),
        # Check if bundled with exe (PyInstaller temp folder)
        os.path.join(sys._MEIPASS, 'tesseract-ocr', 'tesseract.exe') if hasattr(sys, '_MEIPASS') else None,
        # Standard installation paths
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
    ]
    
    # Remove None values
    possible_paths = [p for p in possible_paths if p is not None]
    
    tesseract_found = False
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tesseract_found = True
            break
    
    # If not found in paths, check if it's in system PATH
    if not tesseract_found and check_tesseract_in_path():
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'

class CoordinateExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Lat Long Extractor by Irfan Khaliq")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.image_path = None
        self.image_paths = []  # For batch processing
        self.image_paths_dict = {}  # Map image names to paths for batch processing
        self.extracted_coords = []
        self.all_results = []  # Store all batch results
        self.processing = False  # Flag to prevent multiple simultaneous processing
        self.paused = False  # Flag for pause/resume functionality
        
        # Create main container
        main_container = tk.Frame(root, bg="#f0f0f0")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame
        header_frame = tk.Frame(main_container, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="📍 Lat Long Extractor by Irfan Khaliq", 
                              font=("Arial", 18, "bold"),
                              bg="#2c3e50", fg="white")
        title_label.pack(pady=20)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Single Image Tab
        single_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(single_tab, text="Single Image")
        self.setup_single_image_tab(single_tab)
        
        # Batch Processing Tab
        batch_tab = tk.Frame(notebook, bg="#f0f0f0")
        notebook.add(batch_tab, text="Batch Processing")
        self.setup_batch_tab(batch_tab)
        
        # Status bar
        self.status_frame = tk.Frame(main_container, bg="#34495e", height=30)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Ready", 
                                     fg="white", bg="#34495e", 
                                     font=("Arial", 9),
                                     anchor=tk.W, padx=10)
        self.status_label.pack(fill=tk.X, side=tk.LEFT)
        
    def setup_single_image_tab(self, parent):
        """Setup the single image processing tab"""
        # Left panel for image preview
        left_panel = tk.Frame(parent, bg="#f0f0f0", width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        
        # Image preview frame
        preview_frame = tk.LabelFrame(left_panel, text="Image Preview", 
                                     font=("Arial", 11, "bold"),
                                     bg="#f0f0f0", padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.preview_label = tk.Label(preview_frame, 
                                      text="No image selected",
                                      bg="white", 
                                      fg="gray",
                                      font=("Arial", 10),
                                      width=45, height=15,
                                      relief=tk.SUNKEN)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Image info label
        self.image_info_label = tk.Label(left_panel, 
                                         text="No image selected", 
                                         fg="gray", 
                                         bg="#f0f0f0",
                                         font=("Arial", 9),
                                         wraplength=380,
                                         justify=tk.LEFT)
        self.image_info_label.pack(pady=5, anchor=tk.W)
        
        # Buttons frame
        btn_frame = tk.Frame(left_panel, bg="#f0f0f0")
        btn_frame.pack(fill=tk.X, pady=5)
        
        select_btn = tk.Button(btn_frame, text="📁 Select Image", 
                              command=self.select_image, 
                              font=("Arial", 11, "bold"),
                              bg="#3498db", fg="white",
                              padx=15, pady=8,
                              cursor="hand2",
                              relief=tk.RAISED,
                              bd=2)
        select_btn.pack(fill=tk.X, pady=2)
        
        extract_btn = tk.Button(btn_frame, text="🔍 Extract Coordinates", 
                               command=self.extract_coordinates,
                               font=("Arial", 11, "bold"),
                               bg="#27ae60", fg="white",
                               padx=15, pady=8,
                               cursor="hand2",
                               relief=tk.RAISED,
                               bd=2,
                               state=tk.DISABLED)
        extract_btn.pack(fill=tk.X, pady=2)
        self.extract_btn = extract_btn
        
        save_btn = tk.Button(btn_frame, text="💾 Save to Text File", 
                            command=self.save_to_file,
                            font=("Arial", 11, "bold"),
                            bg="#e67e22", fg="white",
                            padx=15, pady=8,
                            cursor="hand2",
                            relief=tk.RAISED,
                            bd=2,
                            state=tk.DISABLED)
        save_btn.pack(fill=tk.X, pady=2)
        self.save_btn = save_btn
        
        # Right panel for results
        right_panel = tk.Frame(parent, bg="#f0f0f0")
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        results_label = tk.Label(right_panel, text="Extracted Coordinates", 
                                font=("Arial", 12, "bold"),
                                bg="#f0f0f0")
        results_label.pack(pady=(0, 5), anchor=tk.W)
        
        self.results_text = scrolledtext.ScrolledText(right_panel, 
                                                      height=25, 
                                                      width=50,
                                                      font=("Courier", 10),
                                                      wrap=tk.WORD,
                                                      bg="white",
                                                      relief=tk.SUNKEN,
                                                      bd=2)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def setup_batch_tab(self, parent):
        """Setup the batch processing tab"""
        # Top frame for controls
        control_frame = tk.Frame(parent, bg="#f0f0f0")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        select_batch_btn = tk.Button(control_frame, text="📁 Select Multiple Images", 
                                     command=self.select_batch_images,
                                     font=("Arial", 11, "bold"),
                                     bg="#3498db", fg="white",
                                     padx=20, pady=10,
                                     cursor="hand2")
        select_batch_btn.pack(side=tk.LEFT, padx=5)
        
        process_batch_btn = tk.Button(control_frame, text="⚡ Process All Images", 
                                      command=self.process_batch,
                                      font=("Arial", 11, "bold"),
                                      bg="#27ae60", fg="white",
                                      padx=20, pady=10,
                                      cursor="hand2",
                                      state=tk.DISABLED)
        process_batch_btn.pack(side=tk.LEFT, padx=5)
        self.process_batch_btn = process_batch_btn
        
        save_batch_btn = tk.Button(control_frame, text="💾 Save All Results", 
                                   command=self.save_batch_results,
                                   font=("Arial", 11, "bold"),
                                   bg="#e67e22", fg="white",
                                   padx=20, pady=10,
                                   cursor="hand2",
                                   state=tk.DISABLED)
        save_batch_btn.pack(side=tk.LEFT, padx=5)
        self.save_batch_btn = save_batch_btn
        
        pause_batch_btn = tk.Button(control_frame, text="⏸️ Pause", 
                                    command=self.toggle_pause,
                                    font=("Arial", 11, "bold"),
                                    bg="#f39c12", fg="white",
                                    padx=20, pady=10,
                                    cursor="hand2",
                                    state=tk.DISABLED)
        pause_batch_btn.pack(side=tk.LEFT, padx=5)
        self.pause_batch_btn = pause_batch_btn
        
        remove_duplicates_btn = tk.Button(control_frame, text="🔄 Remove Duplicates", 
                                         command=self.remove_duplicates,
                                         font=("Arial", 11, "bold"),
                                         bg="#9b59b6", fg="white",
                                         padx=20, pady=10,
                                         cursor="hand2",
                                         state=tk.DISABLED)
        remove_duplicates_btn.pack(side=tk.LEFT, padx=5)
        self.remove_duplicates_btn = remove_duplicates_btn
        
        clear_batch_btn = tk.Button(control_frame, text="🗑️ Clear List", 
                                    command=self.clear_batch,
                                    font=("Arial", 11),
                                    bg="#e74c3c", fg="white",
                                    padx=20, pady=10,
                                    cursor="hand2")
        clear_batch_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress frame
        progress_frame = tk.Frame(parent, bg="#f0f0f0")
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_label = tk.Label(progress_frame, text="", 
                                       bg="#f0f0f0",
                                       font=("Arial", 9))
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Results frame with treeview
        results_frame = tk.LabelFrame(parent, text="Batch Results", 
                                      font=("Arial", 11, "bold"),
                                      bg="#f0f0f0", padx=10, pady=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for results
        columns = ("Serial", "Image Name", "Latitude", "Longitude", "Status", "View Image")
        self.batch_tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
        
        for col in columns:
            self.batch_tree.heading(col, text=col)
            self.batch_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.batch_tree.column("Image Name", width=200)
        self.batch_tree.column("Status", width=150)
        self.batch_tree.column("View Image", width=100)
        
        # Bind double-click event to view image
        self.batch_tree.bind("<Double-1>", self.on_tree_double_click)
        
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.batch_tree.yview)
        self.batch_tree.configure(yscrollcommand=scrollbar.set)
        
        self.batch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def select_image(self):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.load_image_preview(file_path)
            filename = os.path.basename(file_path)
            self.image_info_label.config(text=f"File: {filename}", fg="black")
            self.extract_btn.config(state=tk.NORMAL)
            self.update_status("Image selected. Click 'Extract Coordinates' to proceed.")
    
    def load_image_preview(self, image_path):
        """Load and display image preview"""
        try:
            image = Image.open(image_path)
            # Resize for preview
            image.thumbnail((350, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo  # Keep a reference
        except Exception as e:
            self.preview_label.config(image="", text=f"Error loading image:\n{str(e)}")
    
    def select_batch_images(self):
        """Select multiple images for batch processing"""
        file_paths = filedialog.askopenfilenames(
            title="Select Multiple Images",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            # Add new images to existing list (avoid duplicates)
            new_paths = []
            for path in file_paths:
                if path not in self.image_paths:
                    self.image_paths.append(path)
                    new_paths.append(path)
                    # Add to mapping
                    img_name = os.path.splitext(os.path.basename(path))[0]
                    self.image_paths_dict[img_name] = path
            
            if new_paths:
                self.process_batch_btn.config(state=tk.NORMAL)
                self.update_status(f"Added {len(new_paths)} new image(s). Total: {len(self.image_paths)} image(s) ready for processing.")
            else:
                messagebox.showinfo("Info", "All selected images are already in the list.")
    
    def clear_batch(self):
        """Clear batch processing list"""
        self.image_paths = []
        self.image_paths_dict = {}
        self.all_results = []
        for item in self.batch_tree.get_children():
            self.batch_tree.delete(item)
        self.process_batch_btn.config(state=tk.DISABLED)
        self.save_batch_btn.config(state=tk.DISABLED)
        self.update_status("Batch list cleared.")
    
    def on_tree_double_click(self, event):
        """Handle double-click on tree item to view image"""
        item = self.batch_tree.selection()[0] if self.batch_tree.selection() else None
        if item:
            values = self.batch_tree.item(item, 'values')
            if len(values) >= 2:
                img_name = values[1]  # Image Name column
                # Find the image path
                image_path = self.image_paths_dict.get(img_name)
                if image_path and os.path.exists(image_path):
                    self.view_image(image_path, img_name)
                else:
                    messagebox.showwarning("Image Not Found", f"Could not find image: {img_name}")
    
    def view_image(self, image_path, image_name):
        """Open image in a new window for verification"""
        try:
            # Create new window
            image_window = tk.Toplevel(self.root)
            image_window.title(f"View Image: {image_name}")
            image_window.geometry("800x600")
            
            # Load and display image
            image = Image.open(image_path)
            
            # Calculate display size (fit to window)
            max_width = 750
            max_height = 550
            
            width, height = image.size
            scale = min(max_width / width, max_height / height, 1.0)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Create frame with scrollbar
            canvas_frame = tk.Frame(image_window)
            canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = tk.Canvas(canvas_frame, bg="white")
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(image_window, orient=tk.HORIZONTAL, command=canvas.xview)
            
            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
            
            # Add image to canvas
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep a reference
            
            # Update scroll region
            canvas.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))
            
            # Add info label
            info_label = tk.Label(image_window, 
                                 text=f"Image: {os.path.basename(image_path)} | Size: {width}x{height}",
                                 font=("Arial", 9),
                                 bg="#f0f0f0")
            info_label.pack(pady=5)
            
            # Add close button
            close_btn = tk.Button(image_window, 
                                 text="Close", 
                                 command=image_window.destroy,
                                 font=("Arial", 10),
                                 bg="#3498db", fg="white",
                                 padx=20, pady=5)
            close_btn.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")
    
    def preprocess_image(self, image):
        """Preprocess image to improve OCR accuracy"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to grayscale for better OCR
        if image.mode == 'RGB':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply filter to reduce noise
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Resize if too small (OCR works better on larger images)
        width, height = image.size
        if width < 800 or height < 600:
            scale = max(800/width, 600/height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def extract_coordinates(self):
        """Extract latitude and longitude from image using OCR (threaded)"""
        if not self.image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        if self.processing:
            messagebox.showwarning("Warning", "Processing already in progress. Please wait.")
            return
        
        # Disable button and set processing flag
        self.processing = True
        self.extract_btn.config(state=tk.DISABLED)
        self.update_status("Processing image with OCR... Please wait.", "info")
        
        # Start processing in separate thread
        thread = threading.Thread(target=self._extract_coordinates_worker, daemon=True)
        thread.start()
    
    def _extract_coordinates_worker(self):
        """Worker method that runs OCR processing in background thread"""
        try:
            # Load image
            original_image = Image.open(self.image_path)
            
            # Preprocess image for better OCR
            processed_image = self.preprocess_image(original_image.copy())
            
            # Also try with original image
            all_texts = []
            
            # Try multiple approaches (reduced to speed up)
            images_to_try = [
                (processed_image, "Processed"),
                (original_image.convert('RGB'), "Original RGB"),
            ]
            
            # Perform OCR with multiple configurations (reduced modes for speed)
            psm_modes = [6, 11, 3]  # Reduced modes for faster processing
            
            for img, img_type in images_to_try:
                for psm in psm_modes:
                    try:
                        custom_config = f'--oem 3 --psm {psm}'
                        text = pytesseract.image_to_string(img, config=custom_config)
                        if text and text.strip():
                            all_texts.append((text, f"{img_type} PSM{psm}"))
                            # Break after first successful OCR per image type
                            break
                    except:
                        continue
            
            # Also try default OCR
            try:
                default_text = pytesseract.image_to_string(original_image)
                if default_text:
                    all_texts.append((default_text, "Default"))
            except:
                pass
            
            # Combine all OCR results
            combined_text = "\n".join([text for text, _ in all_texts])
            
            # Extract coordinates from all texts
            all_coordinates = []
            for text, source in all_texts:
                coords = self.find_coordinates(text)
                all_coordinates.extend(coords)
            
            # Also try combined text
            combined_coords = self.find_coordinates(combined_text)
            all_coordinates.extend(combined_coords)
            
            # Remove duplicates
            unique_coords = []
            for coord in all_coordinates:
                is_duplicate = False
                for existing in unique_coords:
                    if abs(coord[1] - existing[1]) < 0.0001 and abs(coord[2] - existing[2]) < 0.0001:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    unique_coords.append(coord)
            
            # Update UI in main thread
            self.root.after(0, self._extract_coordinates_callback, unique_coords, all_texts, combined_text)
            
        except Exception as e:
            import traceback
            error_msg = f"Failed to process image:\n{str(e)}"
            self.root.after(0, self._extract_coordinates_error_callback, error_msg)
    
    def _extract_coordinates_callback(self, unique_coords, all_texts, combined_text):
        """Callback to update UI after processing completes"""
        self.processing = False
        self.extract_btn.config(state=tk.NORMAL)
        
        if unique_coords:
            self.extracted_coords = unique_coords
            self.display_results(unique_coords)
            self.save_btn.config(state=tk.NORMAL)
            self.update_status(f"Found {len(unique_coords)} coordinate(s)!", "success")
        else:
            self.extracted_coords = []
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "No coordinates found in the image.\n\n")
            self.results_text.insert(tk.END, "=" * 70 + "\n")
            self.results_text.insert(tk.END, "DEBUG: OCR Text Extracted:\n")
            self.results_text.insert(tk.END, "=" * 70 + "\n\n")
            
            # Show all OCR attempts
            for i, (text, source) in enumerate(all_texts, 1):
                self.results_text.insert(tk.END, f"--- Attempt {i} ({source}) ---\n")
                self.results_text.insert(tk.END, text[:500] + ("..." if len(text) > 500 else "") + "\n\n")
            
            if combined_text:
                self.results_text.insert(tk.END, "--- Combined Text ---\n")
                self.results_text.insert(tk.END, combined_text[:1000] + ("..." if len(combined_text) > 1000 else "") + "\n\n")
            
            self.results_text.insert(tk.END, "=" * 70 + "\n")
            self.results_text.insert(tk.END, "Tip: Check the OCR text above. If coordinates are visible, the pattern matching may need adjustment.\n")
            self.save_btn.config(state=tk.DISABLED)
            self.update_status("No coordinates found. Check OCR text above.", "warning")
    
    def _extract_coordinates_error_callback(self, error_msg):
        """Callback to handle errors"""
        self.processing = False
        self.extract_btn.config(state=tk.NORMAL)
        messagebox.showerror("Error", error_msg)
        self.update_status("Error occurred", "error")
    
    def process_batch(self):
        """Process all selected images in batch (threaded)"""
        if not self.image_paths:
            messagebox.showwarning("Warning", "Please select images first.")
            return
        
        if self.processing:
            messagebox.showwarning("Warning", "Processing already in progress. Please wait.")
            return
        
        # Disable button and set processing flag
        self.processing = True
        self.paused = False
        self.process_batch_btn.config(state=tk.DISABLED)
        self.pause_batch_btn.config(state=tk.NORMAL, text="⏸️ Pause")
        
        # Don't clear previous results - append to existing
        # Get current serial number to continue from
        current_serial = len(self.all_results) if self.all_results else 0
        
        # Find which images haven't been processed yet
        processed_image_names = {result['img_name'] for result in self.all_results}
        unprocessed_paths = []
        for path in self.image_paths:
            img_name = os.path.splitext(os.path.basename(path))[0]
            if img_name not in processed_image_names:
                unprocessed_paths.append(path)
        
        if not unprocessed_paths:
            messagebox.showinfo("Info", "All images have already been processed.")
            self.processing = False
            self.process_batch_btn.config(state=tk.NORMAL)
            self.pause_batch_btn.config(state=tk.DISABLED)
            return
        
        total_processed = len(self.all_results)
        total_to_process = len(unprocessed_paths)
        total = len(self.image_paths)
        
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = total_processed
        
        # Start processing in separate thread with unprocessed paths
        thread = threading.Thread(target=self._process_batch_worker, args=(unprocessed_paths, current_serial, total), daemon=True)
        thread.start()
    
    def _process_batch_worker(self, unprocessed_paths, start_serial, total):
        """Worker method for batch processing"""
        serial_no = start_serial + 1
        current_processed = len(self.all_results)
        
        for idx, image_path in enumerate(unprocessed_paths):
            # Check for pause
            while self.paused and self.processing:
                import time
                time.sleep(0.1)
            
            # Check if processing was cancelled
            if not self.processing:
                break
            
            try:
                # Update progress in main thread
                current_processed += 1
                self.root.after(0, self._update_batch_progress, current_processed, total, os.path.basename(image_path))
                
                # Load image
                original_image = Image.open(image_path)
                
                # Preprocess image for better OCR
                processed_image = self.preprocess_image(original_image.copy())
                
                # Try multiple approaches (reduced for speed)
                all_texts = []
                images_to_try = [
                    (processed_image, "Processed"),
                    (original_image.convert('RGB'), "Original RGB"),
                ]
                
                # Perform OCR with reduced configurations for speed
                psm_modes = [6, 11, 3]  # Reduced modes
                
                for img, img_type in images_to_try:
                    for psm in psm_modes:
                        try:
                            custom_config = f'--oem 3 --psm {psm}'
                            text = pytesseract.image_to_string(img, config=custom_config)
                            if text and text.strip():
                                all_texts.append(text)
                                break  # Use first successful OCR
                        except:
                            continue
                
                # Combine all OCR results
                combined_text = "\n".join(all_texts)
                
                # Extract coordinates from all texts
                all_coordinates = []
                for text in all_texts:
                    coords = self.find_coordinates(text)
                    all_coordinates.extend(coords)
                
                # Also try combined text
                combined_coords = self.find_coordinates(combined_text)
                all_coordinates.extend(combined_coords)
                
                # Remove duplicates
                unique_coords = []
                for coord in all_coordinates:
                    is_duplicate = False
                    for existing in unique_coords:
                        if abs(coord[1] - existing[1]) < 0.0001 and abs(coord[2] - existing[2]) < 0.0001:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        unique_coords.append(coord)
                
                coordinates = unique_coords
                img_name = os.path.splitext(os.path.basename(image_path))[0]
                
                # Update UI in main thread
                if coordinates:
                    for format_type, lat, lon in coordinates:
                        result = {
                            'serial': serial_no,
                            'img_name': img_name,
                            'lat': lat,
                            'lon': lon
                        }
                        self.all_results.append(result)
                        self.root.after(0, self._add_batch_result, serial_no, img_name, lat, lon, "✓ Success")
                        serial_no += 1
                        # Update remove duplicates button state
                        self.root.after(0, lambda: self.remove_duplicates_btn.config(state=tk.NORMAL))
                else:
                    self.root.after(0, self._add_batch_result, "-", img_name, None, None, "✗ No coordinates")
                
            except Exception as e:
                img_name = os.path.splitext(os.path.basename(image_path))[0]
                self.root.after(0, self._add_batch_result, "-", img_name, None, None, f"✗ Error: {str(e)[:20]}")
            
            # Check if processing was cancelled
            if not self.processing:
                break
        
        # Finalize in main thread
        self.root.after(0, self._process_batch_complete, total)
    
    def _update_batch_progress(self, current, total, filename):
        """Update progress bar and label"""
        self.progress_label.config(text=f"Processing {current}/{total}: {filename}")
        self.progress_bar['value'] = current
        self.root.update_idletasks()
    
    def _add_batch_result(self, serial_no, img_name, lat, lon, status):
        """Add result to batch tree"""
        if lat is not None and lon is not None:
            self.batch_tree.insert("", tk.END, values=(
                serial_no, img_name, f"{lat:.6f}", f"{lon:.6f}", status, "👁️ Click to View"
            ))
        else:
            self.batch_tree.insert("", tk.END, values=(
                serial_no, img_name, "-", "-", status, "👁️ Click to View"
            ))
    
    def _process_batch_complete(self, total):
        """Callback when batch processing completes"""
        self.processing = False
        self.paused = False
        self.process_batch_btn.config(state=tk.NORMAL)
        self.pause_batch_btn.config(state=tk.DISABLED, text="⏸️ Pause")
        self.remove_duplicates_btn.config(state=tk.NORMAL if self.all_results else tk.DISABLED)
        self.progress_label.config(text=f"Completed: {len(self.all_results)} coordinates found from {total} images")
        self.save_batch_btn.config(state=tk.NORMAL if self.all_results else tk.DISABLED)
        self.update_status(f"Batch processing complete! Found {len(self.all_results)} coordinate(s).", "success")
    
    def toggle_pause(self):
        """Toggle pause/resume for batch processing"""
        if not self.processing:
            return
        
        if self.paused:
            self.paused = False
            self.pause_batch_btn.config(text="⏸️ Pause")
            self.update_status("Processing resumed...", "info")
        else:
            self.paused = True
            self.pause_batch_btn.config(text="▶️ Resume")
            self.update_status("Processing paused. Click Resume to continue.", "warning")
    
    def remove_duplicates(self):
        """Remove duplicate rows from batch results"""
        if not self.all_results:
            messagebox.showwarning("Warning", "No results to check for duplicates.")
            return
        
        # Find duplicates by checking entire row (serial, img_name, lat, lon)
        seen = {}
        duplicates = []
        unique_results = []
        
        for result in self.all_results:
            # Create a key from all fields
            key = (result['serial'], result['img_name'], 
                   round(result['lat'], 6), round(result['lon'], 6))
            
            if key in seen:
                duplicates.append(result)
            else:
                seen[key] = result
                unique_results.append(result)
        
        if not duplicates:
            messagebox.showinfo("No Duplicates", "No duplicate rows found.")
            return
        
        # Show duplicates to user
        dup_count = len(duplicates)
        dup_text = f"Found {dup_count} duplicate row(s):\n\n"
        for i, dup in enumerate(duplicates[:10], 1):  # Show first 10
            dup_text += f"{i}. Serial: {dup['serial']}, Image: {dup['img_name']}, "
            dup_text += f"Lat: {dup['lat']:.6f}, Lon: {dup['lon']:.6f}\n"
        
        if dup_count > 10:
            dup_text += f"\n... and {dup_count - 10} more duplicate(s)"
        
        dup_text += f"\n\nTotal unique rows: {len(unique_results)}\n"
        dup_text += f"Total duplicate rows: {dup_count}\n\n"
        dup_text += "Do you want to remove these duplicates?"
        
        # Ask for confirmation
        response = messagebox.askyesno("Remove Duplicates", dup_text)
        
        if response:
            # Update results
            self.all_results = unique_results
            
            # Rebuild tree with unique results
            for item in self.batch_tree.get_children():
                self.batch_tree.delete(item)
            
            # Re-add unique results to tree
            for result in unique_results:
                self.batch_tree.insert("", tk.END, values=(
                    result['serial'], 
                    result['img_name'], 
                    f"{result['lat']:.6f}", 
                    f"{result['lon']:.6f}", 
                    "✓ Success",
                    "👁️ Click to View"
                ))
            
            # Update serial numbers to be sequential
            for idx, result in enumerate(self.all_results, 1):
                result['serial'] = idx
            
            # Rebuild tree with updated serial numbers
            for item in self.batch_tree.get_children():
                self.batch_tree.delete(item)
            
            for result in self.all_results:
                self.batch_tree.insert("", tk.END, values=(
                    result['serial'], 
                    result['img_name'], 
                    f"{result['lat']:.6f}", 
                    f"{result['lon']:.6f}", 
                    "✓ Success",
                    "👁️ Click to View"
                ))
            
            messagebox.showinfo("Success", f"Removed {dup_count} duplicate row(s).\n{len(unique_results)} unique row(s) remaining.")
            self.update_status(f"Removed {dup_count} duplicate(s). {len(unique_results)} unique row(s) remaining.", "success")
    
    def find_coordinates(self, text):
        """Find latitude and longitude coordinates in text using various patterns"""
        coordinates = []
        
        # Normalize text: replace common OCR errors in numbers only
        text_original = text
        # Fix degree symbols
        text = text.replace('°', '°')
        # Replace newlines with spaces for easier matching
        text_normalized = re.sub(r'\s+', ' ', text)
        
        # Pattern 1: "Lat X° Long Y°" format - Handle same line and multi-line
        # Handle variations: Lat/Latitude, Long/Longitude/Lon/Lng, with/without degree symbol
        patterns = [
            # "Lat 30.045977° Long 73.604948°" - same line
            r'(?:Lat|Latitude|Lal)[:\s]*(\d+\.\d+)[°\s]*(?:Long|Longitude|Lon|Lng|L0ng)[:\s]*(\d+\.\d+)',
            # "Lat: 30.045977 Long: 73.604948" - same line
            r'(?:Lat|Latitude)[:\s]+(\d+\.\d+)[\s]+(?:Long|Longitude|Lon|Lng)[:\s]+(\d+\.\d+)',
            # "Latitude 30.045977 Longitude 73.604948" - same line
            r'(?:Lat|Latitude)[\s]+(\d+\.\d+)[\s]+(?:Long|Longitude|Lon|Lng)[\s]+(\d+\.\d+)',
            # More flexible - any text between numbers
            r'[Ll][Aa][Tt][:\s]*(\d+\.\d+)[°\s]*[Ll][Oo0][Nn][Gg][:\s]*(\d+\.\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_normalized, re.IGNORECASE)
            for match in matches:
                try:
                    lat, lon = float(match[0]), float(match[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        coordinates.append(("Lat/Long", lat, lon))
                except:
                    pass
        
        # Pattern 1b: Multi-line format - "Lat X°" on one line, "Long Y°" on next line
        # This handles cases like:
        # "§ Lat 30.172773° "
        # "Long 73.665911°"
        lat_pattern = r'(?:Lat|Latitude|Lal)[:\s]*(\d+\.\d+)[°\s]*'
        lon_pattern = r'(?:Long|Longitude|Lon|Lng|L0ng)[:\s]*(\d+\.\d+)[°\s]*'
        
        # Find all Lat matches
        lat_matches = re.finditer(lat_pattern, text, re.IGNORECASE | re.MULTILINE)
        for lat_match in lat_matches:
            lat_value = float(lat_match.group(1))
            lat_end = lat_match.end()
            
            # Look for Long within next 200 characters
            remaining_text = text[lat_end:lat_end+200]
            lon_match = re.search(lon_pattern, remaining_text, re.IGNORECASE)
            
            if lon_match:
                lon_value = float(lon_match.group(1))
                if -90 <= lat_value <= 90 and -180 <= lon_value <= 180:
                    coordinates.append(("Lat/Long (multi-line)", lat_value, lon_value))
        
        # Also try with normalized text (spaces instead of newlines)
        lat_matches = re.finditer(lat_pattern, text_normalized, re.IGNORECASE)
        for lat_match in lat_matches:
            lat_value = float(lat_match.group(1))
            lat_end = lat_match.end()
            
            # Look for Long within next 100 characters in normalized text
            remaining_text = text_normalized[lat_end:lat_end+100]
            lon_match = re.search(lon_pattern, remaining_text, re.IGNORECASE)
            
            if lon_match:
                lon_value = float(lon_match.group(1))
                if -90 <= lat_value <= 90 and -180 <= lon_value <= 180:
                    coordinates.append(("Lat/Long (normalized)", lat_value, lon_value))
        
        # Pattern 2: "Latitude: X, Longitude: Y" or "Lat: X, Lon: Y"
        labeled_patterns = [
            r'(?:Latitude|Lat)[:\s]+(-?\d+\.?\d*)[,\s]+(?:Longitude|Long|Lon|Lng)[:\s]+(-?\d+\.?\d*)',
            r'(?:Latitude|Lat)[:\s]+(-?\d+\.?\d*)[\s]+(?:Longitude|Long|Lon|Lng)[:\s]+(-?\d+\.?\d*)',
        ]
        for pattern in labeled_patterns:
            matches = re.findall(pattern, text_original, re.IGNORECASE)
            for match in matches:
                try:
                    lat, lon = float(match[0]), float(match[1])
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        coordinates.append(("Labeled", lat, lon))
                except:
                    pass
        
        # Pattern 3: Look for pairs of decimal numbers that look like coordinates
        # This is more aggressive - find any two decimal numbers near each other
        # Format: number with 4+ decimal places (typical for GPS coordinates)
        coord_pair_patterns = [
            r'(\d{1,2}\.\d{4,})\s+(\d{1,3}\.\d{4,})',  # Two numbers with 4+ decimals
            r'(\d{1,2}\.\d{3,})[,\s]+(\d{1,3}\.\d{3,})',  # With comma
            r'(-?\d{1,2}\.\d{4,})[,\s]+(-?\d{1,3}\.\d{4,})',  # With negatives
        ]
        
        for pattern in coord_pair_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    num1, num2 = float(match[0]), float(match[1])
                    # Try both orders
                    for lat, lon in [(num1, num2), (num2, num1)]:
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            coordinates.append(("Auto-detected", lat, lon))
                            break
                except:
                    pass
        
        # Pattern 4: Decimal degrees separated by comma/space
        decimal_pattern = r'(-?\d{1,2}\.\d{3,})[,\s]+(-?\d{1,3}\.\d{3,})'
        matches = re.findall(decimal_pattern, text)
        for match in matches:
            try:
                lat, lon = float(match[0]), float(match[1])
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    coordinates.append(("Decimal", lat, lon))
            except:
                pass
        
        # Pattern 4: Degrees, minutes, seconds (e.g., 40°42'46"N 74°00'22"W)
        dms_pattern = r'(\d+)[°\s]+(\d+)[\'\s]+(\d+)[\"\s]*([NS])\s+(\d+)[°\s]+(\d+)[\'\s]+(\d+)[\"\s]*([EW])'
        matches = re.findall(dms_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                lat_d, lat_m, lat_s, lat_dir = int(match[0]), int(match[1]), int(match[2]), match[3].upper()
                lon_d, lon_m, lon_s, lon_dir = int(match[4]), int(match[5]), int(match[6]), match[7].upper()
                
                lat = lat_d + lat_m/60 + lat_s/3600
                if lat_dir == 'S':
                    lat = -lat
                
                lon = lon_d + lon_m/60 + lon_s/3600
                if lon_dir == 'W':
                    lon = -lon
                
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    coordinates.append(("DMS", lat, lon))
            except:
                pass
        
        # Pattern 5: Degrees and decimal minutes (e.g., 40°42.767'N 74°00.367'W)
        ddm_pattern = r'(\d+)[°\s]+(\d+\.\d+)[\'\s]*([NS])\s+(\d+)[°\s]+(\d+\.\d+)[\'\s]*([EW])'
        matches = re.findall(ddm_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                lat_d, lat_m, lat_dir = int(match[0]), float(match[1]), match[2].upper()
                lon_d, lon_m, lon_dir = int(match[3]), float(match[4]), match[5].upper()
                
                lat = lat_d + lat_m/60
                if lat_dir == 'S':
                    lat = -lat
                
                lon = lon_d + lon_m/60
                if lon_dir == 'W':
                    lon = -lon
                
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    coordinates.append(("DDM", lat, lon))
            except:
                pass
        
        # Pattern 6: Look for pairs of numbers that could be coordinates
        # This is a fallback for when labels are not clear
        coord_pair_pattern = r'(\d{1,2}\.\d{4,})\s+(\d{1,3}\.\d{4,})'
        matches = re.findall(coord_pair_pattern, text)
        for match in matches:
            try:
                num1, num2 = float(match[0]), float(match[1])
                # Try both orders
                for lat, lon in [(num1, num2), (num2, num1)]:
                    if -90 <= lat <= 90 and -180 <= lon <= 180:
                        coordinates.append(("Auto-detected", lat, lon))
                        break
            except:
                pass
        
        # Remove duplicates (same coordinates within small tolerance)
        unique_coords = []
        for coord in coordinates:
            is_duplicate = False
            for existing in unique_coords:
                if abs(coord[1] - existing[1]) < 0.0001 and abs(coord[2] - existing[2]) < 0.0001:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_coords.append(coord)
        
        return unique_coords
    
    def display_results(self, coordinates):
        """Display extracted coordinates in the text area"""
        self.results_text.delete(1.0, tk.END)
        
        if not coordinates:
            self.results_text.insert(tk.END, "No coordinates found.")
            return
        
        self.results_text.insert(tk.END, f"Found {len(coordinates)} coordinate(s):\n\n")
        
        for i, (format_type, lat, lon) in enumerate(coordinates, 1):
            self.results_text.insert(tk.END, f"Coordinate {i} ({format_type}):\n")
            self.results_text.insert(tk.END, f"  Latitude:  {lat:.6f}\n")
            self.results_text.insert(tk.END, f"  Longitude: {lon:.6f}\n")
            self.results_text.insert(tk.END, f"  Format:    {lat:.6f}, {lon:.6f}\n\n")
    
    def save_to_file(self):
        """Save extracted coordinates to a text file"""
        if not self.extracted_coords:
            messagebox.showwarning("Warning", "No coordinates to save.")
            return
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"coordinates_{timestamp}.txt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Coordinates",
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Get image name without extension
                img_name = os.path.splitext(os.path.basename(self.image_path))[0]
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write("serial no, Img name, lat, long\n")
                    
                    # Write data rows
                    for i, (format_type, lat, lon) in enumerate(self.extracted_coords, 1):
                        f.write(f"{i}, {img_name}, {lat:.6f}, {lon:.6f}\n")
                
                messagebox.showinfo("Success", f"Coordinates saved to:\n{file_path}")
                self.update_status(f"Saved to: {os.path.basename(file_path)}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                self.update_status("Save failed", "error")
    
    def save_batch_results(self):
        """Save all batch processing results to a text file"""
        if not self.all_results:
            messagebox.showwarning("Warning", "No results to save.")
            return
        
        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"batch_coordinates_{timestamp}.txt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Batch Results",
            defaultextension=".txt",
            initialfile=default_filename,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write("serial no, Img name, lat, long\n")
                    
                    # Write data rows
                    for result in self.all_results:
                        f.write(f"{result['serial']}, {result['img_name']}, {result['lat']:.6f}, {result['lon']:.6f}\n")
                
                messagebox.showinfo("Success", 
                                  f"Saved {len(self.all_results)} coordinates to:\n{file_path}")
                self.update_status(f"Batch results saved: {len(self.all_results)} coordinates", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                self.update_status("Save failed", "error")
    
    def update_status(self, message, status_type="info"):
        """Update status bar with message and color"""
        color_map = {
            "info": "white",
            "success": "#2ecc71",
            "warning": "#f39c12",
            "error": "#e74c3c"
        }
        color = color_map.get(status_type, "white")
        self.status_label.config(text=message, fg=color)

def main():
    # Check if Tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        root = tk.Tk()
        root.withdraw()  # Hide main window
        messagebox.showerror(
            "Tesseract OCR Not Found",
            "Tesseract OCR is not installed or not in PATH.\n\n"
            "Please install Tesseract OCR:\n"
            "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Install it and add to PATH\n"
            "3. Restart this application"
        )
        root.destroy()
        return
    
    root = tk.Tk()
    app = CoordinateExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
