import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
from run import process_video
from utils import setup_logger
import webbrowser

logger = setup_logger("gui")

class VideoProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Video Captioning & Documentation")
        self.root.geometry("600x500")
        
        # Variables
        self.input_var = tk.StringVar()
        self.type_var = tk.StringVar(value="local")
        self.whisper_var = tk.StringVar(value="small")
        self.diff_var = tk.DoubleVar(value=0.35)
        self.processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))#type: ignore
        
        # Title
        title_label = ttk.Label(main_frame, text="Meeting Video Captioning & Documentation", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input section
        ttk.Label(main_frame, text="Video Input:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Input type selection
        type_frame = ttk.Frame(main_frame)
        type_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)#type: ignore
        
        ttk.Radiobutton(type_frame, text="Local File", variable=self.type_var, 
                       value="local", command=self.on_type_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="YouTube URL", variable=self.type_var, 
                       value="youtube", command=self.on_type_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(type_frame, text="HTTP URL", variable=self.type_var, 
                       value="http", command=self.on_type_change).pack(side=tk.LEFT)
        
        # Input field and browse button
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)#type: ignore
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=50)
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))#type: ignore
        
        self.browse_btn = ttk.Button(input_frame, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=0, column=1)
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)#type: ignore
        settings_frame.columnconfigure(1, weight=1)
        
        # Whisper model
        ttk.Label(settings_frame, text="Whisper Model:").grid(row=0, column=0, sticky=tk.W, pady=2)
        whisper_combo = ttk.Combobox(settings_frame, textvariable=self.whisper_var, 
                                   values=["tiny", "base", "small", "medium", "large"], 
                                   state="readonly", width=15)
        whisper_combo.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Diff threshold
        ttk.Label(settings_frame, text="Scene Change Threshold:").grid(row=1, column=0, sticky=tk.W, pady=2)
        diff_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, variable=self.diff_var, 
                              orient=tk.HORIZONTAL, length=200)
        diff_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2) #type: ignore
        
        ttk.Label(settings_frame, textvariable=self.diff_var).grid(row=1, column=2, sticky=tk.W, pady=2)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="🎬 Process Video (Single Click)", 
                                     command=self.start_processing, style="Accent.TButton")
        self.process_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5) #type: ignore
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to process video", 
                                     foreground="green")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5)
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)#type: ignore
        results_frame.columnconfigure(1, weight=1)
        
        self.captioned_label = ttk.Label(results_frame, text="Captioned Video: Not generated")
        self.captioned_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        self.report_label = ttk.Label(results_frame, text="Report: Not generated")
        self.report_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Open buttons
        self.open_video_btn = ttk.Button(results_frame, text="Open Video", 
                                        command=self.open_video, state="disabled")
        self.open_video_btn.grid(row=2, column=0, pady=5, padx=(0, 5))
        
        self.open_report_btn = ttk.Button(results_frame, text="Open Report", 
                                         command=self.open_report, state="disabled")
        self.open_report_btn.grid(row=2, column=1, pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self.results = None
        
    def on_type_change(self):
        # Always enable input field
        self.input_entry.config(state="normal")
        # Enable browse only for local files
        if self.type_var.get() == "local":
            self.browse_btn.config(state="normal")
        else:
            self.browse_btn.config(state="disabled")
            
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv *.wmv"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
            
    def start_processing(self):
        if not self.input_var.get().strip():
            messagebox.showerror("Error", "Please select a video file or enter a URL")
            return
            
        if self.processing:
            return
            
        # Start processing in a separate thread
        self.processing = True
        self.process_btn.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Processing video...", foreground="blue")
        
        thread = threading.Thread(target=self.process_video_thread)
        thread.daemon = True
        thread.start()
        
    def process_video_thread(self):
        try:
            self.results = process_video(
                self.input_var.get().strip(),
                source_type=self.type_var.get(),
                whisper_model=self.whisper_var.get(),
                diff_threshold=self.diff_var.get()
            )
            
            # Update UI in main thread
            self.root.after(0, self.processing_complete)
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            error_msg = str(e)
            self.root.after(0, lambda msg=error_msg: self.processing_failed(msg))
            
    def processing_complete(self):
        self.processing = False
        self.process_btn.config(state="normal")
        self.progress.stop()
        self.status_label.config(text="Processing completed successfully!", foreground="green")
        
        # Update result labels
        if self.results:
            captioned_path = Path(self.results["captioned"]).name
            report_path = Path(self.results["report"]).name
            
            self.captioned_label.config(text=f"Captioned Video: {captioned_path}")
            self.report_label.config(text=f"Report: {report_path}")
            
            self.open_video_btn.config(state="normal")
            self.open_report_btn.config(state="normal")
            
        messagebox.showinfo("Success", "Video processing completed successfully!")
        
    def processing_failed(self, error_msg):
        self.processing = False
        self.process_btn.config(state="normal")
        self.progress.stop()
        self.status_label.config(text="Processing failed", foreground="red")
        messagebox.showerror("Processing Failed", f"An error occurred:\n{error_msg}")
        
    def open_video(self):
        if self.results and "captioned" in self.results:
            try:
                webbrowser.open(f"file://{Path(self.results['captioned']).resolve()}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open video: {e}")
                
    def open_report(self):
        if self.results and "report" in self.results:
            try:
                webbrowser.open(f"file://{Path(self.results['report']).resolve()}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open report: {e}")

def main():
    root = tk.Tk()
    app = VideoProcessorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()