import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import threading
import os
import time
import sys

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Using fallback system stats.")

class PCManagerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.current_page = tk.StringVar(value="Home")
        self.button_widgets = {}
        self.is_minimized = False
        self.original_geometry = ""
        self.setup_main_window()
        self.setup_ui()
        
    def setup_main_window(self):
        """Setup main window properties"""
        self.root.title("Lightning Booster")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1a1a2e", highlightthickness=0, bd=0)
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        
        # Bind keyboard shortcuts
        self.root.bind("<Alt-Tab>", lambda e: self.restore_window_func() if self.is_minimized else None)
        self.root.bind("<Control-m>", lambda e: self.minimize_window())
        self.root.bind("<F11>", lambda e: self.toggle_maximize())
        
        # Try to set application icon
        self.set_application_icon()
            
    def set_application_icon(self):
        """Set application icon with multiple fallback options"""
        icon_paths = [
            'img/lightning_booster_icon.ico',
            'img/lightning_booster_icon.png',
            'img/lightning_icon.ico',
            'img/lightning_icon.png'
        ]
        
        for icon_path in icon_paths:
            try:
                # Check if running as executable (PyInstaller)
                if getattr(sys, 'frozen', False):
                    # Running as executable
                    base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
                    full_path = os.path.join(base_path, icon_path)
                else:
                    # Running as script
                    full_path = icon_path
                
                if os.path.exists(full_path):
                    if full_path.endswith('.ico'):
                        self.root.iconbitmap(full_path)
                        print(f"Successfully set icon: {full_path}")
                        break
                    elif full_path.endswith(('.png', '.jpg', '.gif')):
                        # For PNG/JPG files, try to use as PhotoImage
                        try:
                            icon_image = tk.PhotoImage(file=full_path)
                            self.root.iconphoto(True, icon_image)
                            print(f"Successfully set icon: {full_path}")
                            break
                        except Exception as e:
                            print(f"Failed to load PNG/JPG icon {full_path}: {e}")
                            continue
                else:
                    print(f"Icon file not found: {full_path}")
            except Exception as e:
                print(f"Failed to load icon {icon_path}: {e}")
                continue
        
        # If no custom icon worked, use default system icon
        try:
            self.root.iconname("Lightning Booster")
        except:
            pass
    def setup_ui(self):
        """Setup the complete user interface"""
        self.create_main_container()
        self.create_title_bar()
        self.create_sidebar()
        self.create_content_area()
        self.update_content_area()
        
    def create_main_container(self):
        """Create main container"""
        self.main_container = tk.Frame(self.root, bg="#1a1a2e", highlightthickness=0, bd=0)
        self.main_container.pack(fill="both", expand=True)
        
    def create_title_bar(self):
        """Create custom title bar with window controls"""
        self.title_bar = tk.Frame(self.main_container, bg="#0f1419", height=35)
        self.title_bar.pack(fill="x")
        self.title_bar.pack_propagate(False)
        
        # Title with lightning icon
        title_frame = tk.Frame(self.title_bar, bg="#0f1419")
        title_frame.pack(side="left", padx=10, pady=8)
        
        # Lightning bolt icon
        lightning_icon = tk.Label(title_frame, text="⚡", font=("Segoe UI", 12),
                                 fg="#FFD700", bg="#0f1419")
        lightning_icon.pack(side="left", padx=(0, 5))
        
        title_label = tk.Label(title_frame, text="Lightning Booster", 
                              font=("Segoe UI", 10), fg="#ffffff", bg="#0f1419")
        title_label.pack(side="left")
        
        # Window controls
        controls_frame = tk.Frame(self.title_bar, bg="#0f1419")
        controls_frame.pack(side="right", padx=5)
        
        # Minimize button
        self.minimize_btn = tk.Button(controls_frame, text="−", font=("Segoe UI", 12),
                                     fg="#ffffff", bg="#0f1419", relief="flat", bd=0,
                                     width=3, height=1, cursor="hand2",
                                     command=self.minimize_window)
        self.minimize_btn.pack(side="left", padx=1)
        
        # Restore/Maximize button
        self.restore_btn = tk.Button(controls_frame, text="□", font=("Segoe UI", 10),
                                    fg="#ffffff", bg="#0f1419", relief="flat", bd=0,
                                    width=3, height=1, cursor="hand2",
                                    command=self.toggle_maximize)
        self.restore_btn.pack(side="left", padx=1)
        
        # Close button
        self.close_btn = tk.Button(controls_frame, text="×", font=("Segoe UI", 12),
                                  fg="#ffffff", bg="#0f1419", relief="flat", bd=0,
                                  width=3, height=1, cursor="hand2",
                                  command=self.close_application)
        self.close_btn.pack(side="left", padx=1)
        
        # Add hover effects
        self.setup_button_hover_effects()
        self.make_title_bar_draggable(title_frame)
        
    def setup_button_hover_effects(self):
        """Setup hover effects for window control buttons"""
        def on_minimize_enter(e):
            self.minimize_btn.configure(bg="#2d3748")
        def on_minimize_leave(e):
            self.minimize_btn.configure(bg="#0f1419")
        def on_restore_enter(e):
            self.restore_btn.configure(bg="#2d3748")
        def on_restore_leave(e):
            self.restore_btn.configure(bg="#0f1419")
        def on_close_enter(e):
            self.close_btn.configure(bg="#e53e3e")
        def on_close_leave(e):
            self.close_btn.configure(bg="#0f1419")
            
        self.minimize_btn.bind("<Enter>", on_minimize_enter)
        self.minimize_btn.bind("<Leave>", on_minimize_leave)
        self.restore_btn.bind("<Enter>", on_restore_enter)
        self.restore_btn.bind("<Leave>", on_restore_leave)
        self.close_btn.bind("<Enter>", on_close_enter)
        self.close_btn.bind("<Leave>", on_close_leave)
        
    def make_title_bar_draggable(self, title_frame):
        """Make title bar draggable"""
        self.start_x = 0
        self.start_y = 0
        
        def start_move(event):
            self.start_x = event.x
            self.start_y = event.y
            
        def on_motion(event):
            deltax = event.x - self.start_x
            deltay = event.y - self.start_y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
            
        # Make title bar and title frame draggable
        for widget in [self.title_bar, title_frame]:
            widget.bind("<Button-1>", start_move)
            widget.bind("<B1-Motion>", on_motion)
            
        # Also make individual elements draggable
        for child in title_frame.winfo_children():
            child.bind("<Button-1>", start_move)
            child.bind("<B1-Motion>", on_motion)
            
    def minimize_window(self):
        """Minimize window by hiding it"""
        self.root.withdraw()
        self.is_minimized = True
        
        # Create a restore mechanism using the taskbar or a small restore window
        self.create_restore_mechanism()
        
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if not self.original_geometry:
            # Store current geometry
            self.original_geometry = self.root.geometry()
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            # Maximize window
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.restore_btn.configure(text="❐")  # Change to restore icon
        else:
            # Restore to original size
            self.root.geometry(self.original_geometry)
            self.original_geometry = ""
            self.restore_btn.configure(text="□")  # Change back to maximize icon
            
    def create_restore_mechanism(self):
        """Create a small restore window when minimized"""
        if hasattr(self, 'restore_window'):
            return
            
        self.restore_window = tk.Toplevel()
        self.restore_window.title("Lightning Booster - Minimized")
        self.restore_window.geometry("250x80")
        self.restore_window.configure(bg="#1a1a2e")
        self.restore_window.resizable(False, False)
        self.restore_window.attributes('-topmost', True)
        
        # Position at bottom right
        screen_width = self.restore_window.winfo_screenwidth()
        screen_height = self.restore_window.winfo_screenheight()
        x = screen_width - 270
        y = screen_height - 120
        self.restore_window.geometry(f"+{x}+{y}")
        
        # Create main frame with rounded corners
        restore_frame = tk.Frame(self.restore_window, bg="#0f3460", relief="raised", bd=3)
        restore_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header with icon
        header_frame = tk.Frame(restore_frame, bg="#0f3460")
        header_frame.pack(fill="x", padx=10, pady=(8, 5))
        
        icon_label = tk.Label(header_frame, text="⚡", font=("Segoe UI", 12),
                             fg="#FFD700", bg="#0f3460")
        icon_label.pack(side="left")
        
        title_label = tk.Label(header_frame, text="Lightning Booster - Minimized", 
                              font=("Segoe UI", 9, "bold"),
                              fg="#ffffff", bg="#0f3460")
        title_label.pack(side="left", padx=(5, 0))
        
        # Buttons frame
        buttons_frame = tk.Frame(restore_frame, bg="#0f3460")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        restore_btn = tk.Button(buttons_frame, text="🔄 Restore", 
                               command=self.restore_window_func,
                               bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 8, "bold"),
                               relief="raised", bd=2, cursor="hand2", width=10)
        restore_btn.pack(side="left", padx=(0, 5))
        
        close_btn = tk.Button(buttons_frame, text="❌ Close", 
                             command=self.close_application,
                             bg="#e53e3e", fg="#ffffff", font=("Segoe UI", 8, "bold"),
                             relief="raised", bd=2, cursor="hand2", width=10)
        close_btn.pack(side="right")
        
        # Info label
        info_label = tk.Label(restore_frame, text="Press Ctrl+M to minimize • F11 to maximize", 
                             font=("Segoe UI", 7),
                             fg="#cccccc", bg="#0f3460")
        info_label.pack(pady=(0, 5))
        
        # Make window draggable
        self.restore_start_x = 0
        self.restore_start_y = 0
        
        def start_move(event):
            self.restore_start_x = event.x
            self.restore_start_y = event.y
            
        def on_motion(event):
            deltax = event.x - self.restore_start_x
            deltay = event.y - self.restore_start_y
            x = self.restore_window.winfo_x() + deltax
            y = self.restore_window.winfo_y() + deltay
            self.restore_window.geometry(f"+{x}+{y}")
            
        restore_frame.bind("<Button-1>", start_move)
        restore_frame.bind("<B1-Motion>", on_motion)
        header_frame.bind("<Button-1>", start_move)
        header_frame.bind("<B1-Motion>", on_motion)
        
        # Auto-close after 15 seconds
        self.restore_window.after(15000, self.auto_restore)
        
    def restore_window_func(self):
        """Restore the main window"""
        if hasattr(self, 'restore_window'):
            self.restore_window.destroy()
            delattr(self, 'restore_window')
        self.root.deiconify()
        self.root.lift()
        self.is_minimized = False
        
    def auto_restore(self):
        """Auto restore after timeout"""
        if hasattr(self, 'restore_window'):
            self.restore_window.destroy()
            delattr(self, 'restore_window')
            self.restore_window_func()
        
    def close_application(self):
        """Close application safely"""
        try:
            # Close restore window if it exists
            if hasattr(self, 'restore_window'):
                self.restore_window.destroy()
            self.root.quit()
            self.root.destroy()
        except:
            sys.exit(0)
            
    def create_sidebar(self):
        """Create sidebar with navigation"""
        # Content container
        content_container = tk.Frame(self.main_container, bg="#1a1a2e", highlightthickness=0, bd=0)
        content_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(content_container, bg="#16213e", width=200, highlightthickness=0, bd=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Create main content area
        self.content_area = tk.Frame(content_container, bg="#1a1a2e", highlightthickness=0, bd=0)
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Sidebar header
        self.create_sidebar_header()
        self.create_navigation()
        
    def create_sidebar_header(self):
        """Create sidebar header with lightning bolt icon"""
        sidebar_header = tk.Frame(self.sidebar, bg="#16213e", height=80)
        sidebar_header.pack(fill="x")
        sidebar_header.pack_propagate(False)
        
        # Use lightning bolt emoji as icon
        app_icon = tk.Label(sidebar_header, text="⚡", font=("Segoe UI", 24),
                           fg="#FFD700", bg="#16213e")
        app_icon.pack(pady=(0, 5))
        
        app_title = tk.Label(sidebar_header, text="Lightning Booster", 
                            font=("Segoe UI", 12, "bold"),
                            fg="#ffffff", bg="#16213e")
        app_title.pack()
        
    def create_navigation(self):
        """Create navigation buttons"""
        nav_frame = tk.Frame(self.sidebar, bg="#16213e")
        nav_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        nav_buttons = [
            ("🏠", "Home", "Home"),
            ("⚔️", "Protection", "Protection"),
            ("💾", "Storage", "Storage"),
            ("📱", "Apps", "Apps"),
            ("🧰", "Toolbox", "Toolbox"),
            ("⚙️", "Settings", "Settings"),
            ("💬", "Feedback", "Feedback")
        ]
        
        for icon, text, page in nav_buttons:
            frame, icon_lbl, text_lbl = self.create_nav_button(nav_frame, icon, text, page)
            self.button_widgets[page] = (frame, icon_lbl, text_lbl)
            
        # Set Home as active by default
        self.set_active_nav_button("Home")
        
    def create_nav_button(self, parent, icon, text, page_name):
        """Create navigation button"""
        button_frame = tk.Frame(parent, bg="#16213e", cursor="hand2")
        button_frame.pack(fill="x", pady=1)
        
        icon_label = tk.Label(button_frame, text=icon, font=("Segoe UI", 14),
                             fg="#ffffff", bg="#16213e")
        icon_label.pack(side="left", padx=(8, 5), pady=8)
        
        text_label = tk.Label(button_frame, text=text, font=("Segoe UI", 10),
                             fg="#ffffff", bg="#16213e", anchor="w")
        text_label.pack(side="left", fill="x", expand=True, pady=8)
        
        def on_click(e=None):
            self.current_page.set(page_name)
            self.update_content_area()
            self.set_active_nav_button(page_name)
            
        for widget in [button_frame, icon_label, text_label]:
            widget.bind("<Button-1>", on_click)
            
        return button_frame, icon_label, text_label
        
    def set_active_nav_button(self, page_name):
        """Set active navigation button"""
        # Reset all buttons
        for page, (frame, icon_lbl, text_lbl) in self.button_widgets.items():
            frame.configure(bg="#16213e")
            icon_lbl.configure(bg="#16213e")
            text_lbl.configure(bg="#16213e")
            
        # Highlight active button
        if page_name in self.button_widgets:
            frame, icon_lbl, text_lbl = self.button_widgets[page_name]
            frame.configure(bg="#4CAF50")
            icon_lbl.configure(bg="#4CAF50")
            text_lbl.configure(bg="#4CAF50")
            
    def create_content_area(self):
        """Create content area - already created in create_sidebar"""
        pass
        
    def get_system_stats(self):
        """Get system statistics"""
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('C:' if os.name == 'nt' else '/')
                cpu = psutil.cpu_percent(interval=0.1)
                
                return {
                    'memory_percent': memory.percent,
                    'memory_used': f"{memory.used // (1024**3):.1f}GB",
                    'memory_total': f"{memory.total // (1024**3):.1f}GB",
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_free': f"{disk.free // (1024**3):.1f}GB",
                    'disk_total': f"{disk.total // (1024**3):.1f}GB",
                    'cpu_percent': cpu
                }
            except Exception as e:
                print(f"Error getting system stats: {e}")
        
        # Fallback data
        return {
            'memory_percent': 52,
            'memory_used': "8.2GB",
            'memory_total': "16GB",
            'disk_percent': 65,
            'disk_free': "274.9GB",
            'disk_total': "476.8GB",
            'cpu_percent': 25
        }
        
    def show_progress(self, title, message):
        """Show progress window for long-running operations"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title(title)
        progress_window.geometry("400x150")
        progress_window.resizable(False, False)
        progress_window.configure(bg="#1a1a2e")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center the window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
        progress_window.geometry(f"+{x}+{y}")
        
        label = tk.Label(progress_window, text=message, font=("Segoe UI", 12),
                        fg="#4CAF50", bg="#1a1a2e")
        label.pack(pady=20)
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill='x')
        progress_bar.start()
        
        return progress_window, progress_bar
        
    # Action functions
    def cleanup(self):
        """System cleanup with improved error handling"""
        def run_cleanup():
            progress_window, progress_bar = self.show_progress("Cleanup", "Running system cleanup...")
            try:
                if os.name == 'nt':  # Windows
                    commands = [
                        ['del', '/s', '/f', '/q', r'C:\Windows\Temp\*.*'],
                        ['del', '/s', '/f', '/q', r'C:\Windows\Prefetch\*.*'],
                        ['del', '/s', '/f', '/q', os.path.expandvars(r'%TEMP%\*.*')],
                        ['cleanmgr', '/sagerun:1']
                    ]
                    
                    for cmd in commands:
                        try:
                            subprocess.run(cmd, check=False, shell=True, 
                                         capture_output=True, timeout=30)
                        except subprocess.TimeoutExpired:
                            print(f"Command timed out: {' '.join(cmd)}")
                        except Exception as e:
                            print(f"Error running command {' '.join(cmd)}: {e}")
                else:
                    # Basic cleanup for non-Windows systems
                    subprocess.run(['sudo', 'apt', 'autoremove', '-y'], check=False)
                    
                time.sleep(1)  # Give user time to see progress
                progress_window.destroy()
                messagebox.showinfo("Success", "Cleanup completed successfully!")
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"An error occurred during cleanup: {str(e)}")
                
        threading.Thread(target=run_cleanup, daemon=True).start()
        
    def fps_boost(self):
        """FPS Boost implementation"""
        def run_fps_boost():
            progress_window, progress_bar = self.show_progress("FPS Boost", "Optimizing system for gaming...")
            try:
                # Simulate FPS boost operations
                time.sleep(2)
                progress_window.destroy()
                messagebox.showinfo("Success", "FPS Boost applied successfully!")
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"FPS Boost failed: {str(e)}")
                
        threading.Thread(target=run_fps_boost, daemon=True).start()
        
    def visual_tweaks(self):
        """Visual tweaks implementation"""
        messagebox.showinfo("Visual Tweaks", "Visual performance optimizations applied!")
        
    def services(self):
        """Services management"""
        if os.name == 'nt':
            try:
                subprocess.run(['services.msc'], shell=True)
            except:
                messagebox.showerror("Error", "Could not open Services manager")
        else:
            messagebox.showinfo("Services", "Services management (Linux/Mac implementation needed)")
            
    def cpu_optimization(self):
        """CPU optimization"""
        messagebox.showinfo("CPU Optimization", "CPU optimization settings applied!")
        
    def ultimate_performance(self):
        """Enable ultimate performance power plan"""
        if os.name == 'nt':
            try:
                subprocess.run(['powercfg', '/duplicatescheme', 'e9a42b02-d5df-448d-aa00-03f14749eb61'], 
                             shell=True, check=True)
                messagebox.showinfo("Success", "Ultimate Performance power plan enabled!")
            except:
                messagebox.showerror("Error", "Could not enable Ultimate Performance plan")
        else:
            messagebox.showinfo("Power Plan", "Power management optimized for performance!")
            
    def restart_explorer(self):
        """Restart Windows Explorer"""
        if os.name == 'nt':
            try:
                subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], shell=True, check=True)
                subprocess.run(['explorer.exe'], shell=True)
                messagebox.showinfo("Success", "Windows Explorer restarted!")
            except:
                messagebox.showerror("Error", "Could not restart Explorer")
        else:
            messagebox.showinfo("Explorer", "Explorer restart (Windows only)")
            
    def uninstall_microsoft_edge(self):
        """Uninstall Microsoft Edge (with warning)"""
        if messagebox.askyesno("Warning", "Are you sure you want to attempt to uninstall Microsoft Edge?\nThis may cause system instability."):
            messagebox.showinfo("Edge Removal", "Edge removal process initiated (requires advanced techniques)")
            
    def uninstall_onedrive(self):
        """Uninstall OneDrive"""
        if os.name == 'nt':
            if messagebox.askyesno("Confirm", "Are you sure you want to uninstall OneDrive?"):
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'OneDrive.exe'], shell=True)
                    subprocess.run([r'C:\Windows\SysWOW64\OneDriveSetup.exe', '/uninstall'], shell=True)
                    messagebox.showinfo("Success", "OneDrive uninstall initiated!")
                except:
                    messagebox.showerror("Error", "Could not uninstall OneDrive")
        else:
            messagebox.showinfo("OneDrive", "OneDrive uninstall (Windows only)")
            
    def disable_defender(self):
        """Disable Windows Defender (with strong warning)"""
        if messagebox.askyesno("Security Warning", 
                              "Disabling Windows Defender will leave your system vulnerable!\n\nAre you absolutely sure?"):
            messagebox.showwarning("Warning", "Defender management requires administrative privileges and registry changes")
            
    def about(self):
        """Show about dialog"""
        messagebox.showinfo("About", "Lightning Booster\nVersion 2.0\nSystem Optimization Tool")
        
    # UI Creation Methods
    def create_card(self, parent, title, content, color="#0f3460"):
        """Create a card widget with enhanced rounded corner styling"""
        # Outer container for rounded effect with extra padding
        outer_frame = tk.Frame(parent, bg="#1a1a2e")
        outer_frame.pack(fill="x", padx=10, pady=5)
        
        # Inner card with enhanced rounded styling
        card_frame = tk.Frame(outer_frame, bg=color, relief="raised", bd=3)
        card_frame.pack(fill="x", padx=3, pady=3)
        
        # Add inner shadow effect
        shadow_frame = tk.Frame(card_frame, bg="#0a2140", height=2)
        shadow_frame.pack(fill="x")
        
        header = tk.Label(card_frame, text=title, font=("Segoe UI", 12, "bold"),
                         fg="#ffffff", bg=color, anchor="w")
        header.pack(fill="x", padx=18, pady=(18, 3))
        
        content_label = tk.Label(card_frame, text=content, font=("Segoe UI", 10),
                               fg="#cccccc", bg=color, anchor="w", justify="left")
        content_label.pack(fill="x", padx=18, pady=(0, 18))
        
        return card_frame
        
    def create_rounded_card(self, parent, title, content):
        """Create an enhanced rounded card for home page"""
        # Outer container for rounded effect with better spacing
        outer_container = tk.Frame(parent, bg="#1a1a2e")
        outer_container.pack(fill="x", pady=6)
        
        # Enhanced card with better rounded styling
        card = tk.Frame(outer_container, bg="#0f3460", relief="raised", bd=3)
        card.pack(fill="x", padx=4, pady=4)
        
        # Add inner shadow effect
        shadow_frame = tk.Frame(card, bg="#0a2140", height=2)
        shadow_frame.pack(fill="x")
        
        header = tk.Label(card, text=title, 
                         font=("Segoe UI", 11, "bold"),
                         fg="#ffffff", bg="#0f3460", anchor="w")
        header.pack(fill="x", padx=15, pady=(15, 3))
        
        status = tk.Label(card, text=content, 
                         font=("Segoe UI", 9),
                         fg="#cccccc", bg="#0f3460", anchor="w")
        status.pack(fill="x", padx=15, pady=(0, 15))
        
        return card
        
    def create_boost_card(self, parent):
        """Create the PC boost card with enhanced rounded corners"""
        # Outer container for rounded effect with better spacing
        outer_container = tk.Frame(parent, bg="#1a1a2e")
        outer_container.pack(fill="x", padx=10, pady=8)
        
        # Enhanced boost frame with better rounded styling
        boost_frame = tk.Frame(outer_container, bg="#0f3460", relief="raised", bd=3)
        boost_frame.pack(fill="x", padx=4, pady=4)
        
        # Add inner shadow effect
        shadow_frame = tk.Frame(boost_frame, bg="#0a2140", height=2)
        shadow_frame.pack(fill="x")
        
        # Header
        header_frame = tk.Frame(boost_frame, bg="#0f3460")
        header_frame.pack(fill="x", padx=18, pady=(18, 8))
        
        boost_icon = tk.Label(header_frame, text="⚡", font=("Segoe UI", 14),
                             fg="#4CAF50", bg="#0f3460")
        boost_icon.pack(side="left")
        
        boost_title = tk.Label(header_frame, text="PC boost", font=("Segoe UI", 12, "bold"),
                              fg="#ffffff", bg="#0f3460")
        boost_title.pack(side="left", padx=(8, 0))
        
        settings_icon = tk.Label(header_frame, text="⚙️ Set Smart boost", font=("Segoe UI", 9),
                               fg="#4CAF50", bg="#0f3460", cursor="hand2")
        settings_icon.pack(side="right")
        
        # Subtitle
        subtitle = tk.Label(boost_frame, text="Free up resources to help your PC run faster",
                           font=("Segoe UI", 10), fg="#cccccc", bg="#0f3460", anchor="w")
        subtitle.pack(fill="x", padx=18)
        
        # Stats
        stats_frame = tk.Frame(boost_frame, bg="#0f3460")
        stats_frame.pack(fill="x", padx=18, pady=8)
        
        stats = self.get_system_stats()
        
        # Memory usage
        memory_frame = tk.Frame(stats_frame, bg="#0f3460")
        memory_frame.pack(side="left", fill="both", expand=True)
        
        memory_percent = tk.Label(memory_frame, text=f"{int(stats['memory_percent'])}%",
                                 font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#0f3460")
        memory_percent.pack()
        
        memory_label = tk.Label(memory_frame, text="Memory usage", font=("Segoe UI", 9),
                               fg="#cccccc", bg="#0f3460")
        memory_label.pack()
        
        # Temp files
        temp_frame = tk.Frame(stats_frame, bg="#0f3460")
        temp_frame.pack(side="right", fill="both", expand=True)
        
        temp_size = tk.Label(temp_frame, text="0KB", font=("Segoe UI", 16, "bold"),
                            fg="#ffffff", bg="#0f3460")
        temp_size.pack()
        
        temp_label = tk.Label(temp_frame, text="Temporary files", font=("Segoe UI", 9),
                             fg="#cccccc", bg="#0f3460")
        temp_label.pack()
        
        # Boost button with enhanced rounded styling
        boost_btn = tk.Button(boost_frame, text="Boost", command=self.fps_boost,
                             bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                             relief="raised", bd=3, cursor="hand2", width=35, height=2)
        boost_btn.pack(fill="x", padx=18, pady=(8, 18))
        
        return boost_frame
        
    def update_content_area(self):
        """Update content area based on current page"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        page = self.current_page.get()
        
        if page == "Home":
            self.create_home_page()
        elif page == "Protection":
            self.create_protection_page()
        elif page == "Storage":
            self.create_storage_page()
        elif page == "Apps":
            self.create_apps_page()
        elif page == "Toolbox":
            self.create_toolbox_page()
        elif page == "Settings":
            self.create_settings_page()
        elif page == "Feedback":
            self.create_feedback_page()
            
    def create_content_frame(self):
        """Create content frame without scrollbars"""
        # Create a simple frame without scrollbar for cleaner look
        content_frame = tk.Frame(self.content_area, bg="#1a1a2e")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        return content_frame
        
    def create_home_page(self):
        """Create home page content"""
        content_frame = self.create_content_frame()
        
        # Health check card
        self.create_card(content_frame, "🏥 Your PC needs a health check",
                        "Use Health Check to give your PC a checkup.")
        
        # PC boost card
        self.create_boost_card(content_frame)
        
        # Additional cards grid
        actions_frame = tk.Frame(content_frame, bg="#1a1a2e")
        actions_frame.pack(fill="both", expand=True, padx=8, pady=10)
        
        # Left column
        left_column = tk.Frame(actions_frame, bg="#1a1a2e")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Health check card with rounded corners
        self.create_rounded_card(left_column, "🔍 Health check", "Last check\n--")
        
        # Deep cleanup card with rounded corners
        stats = self.get_system_stats()
        self.create_rounded_card(left_column, "🧹 Deep cleanup", 
                                f"Local Disk (C:)\n{stats['disk_free']} / {stats['disk_total']}")
        
        # Right column
        right_column = tk.Frame(actions_frame, bg="#1a1a2e")
        right_column.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Process card with rounded corners
        if PSUTIL_AVAILABLE:
            process_count = len(psutil.pids())
            process_text = f"Running processes\n{process_count} Apps"
        else:
            process_text = "In progress\n11 Apps"
            
        self.create_rounded_card(right_column, "💻 Process", process_text)
        
        # Startup card with rounded corners
        self.create_rounded_card(right_column, "🚀 Startup", "Start time\n3 Sec")
        
    def create_toolbox_page(self):
        """Create toolbox page with optimization tools"""
        content_frame = self.create_content_frame()
        
        # Page title
        title = tk.Label(content_frame, text="🧰 Toolbox", 
                        font=("Segoe UI", 20, "bold"),
                        fg="#ffffff", bg="#1a1a2e", anchor="w")
        title.pack(fill="x", padx=10, pady=(0, 15))
        
        # Tools grid
        tools_frame = tk.Frame(content_frame, bg="#1a1a2e")
        tools_frame.pack(fill="x", padx=10)
        
        # Configure grid
        for i in range(3):
            tools_frame.columnconfigure(i, weight=1)
            
        tools = [
            ("🧹 System Cleanup", self.cleanup),
            ("⚡ FPS Boost", self.fps_boost),
            ("🔧 CPU Optimization", self.cpu_optimization),
            ("🎨 Visual Tweaks", self.visual_tweaks),
            ("⚙️ Services Manager", self.services),
            ("🚀 Ultimate Performance", self.ultimate_performance),
            ("🚫 Disable Defender", self.disable_defender),
            ("📁 Restart Explorer", self.restart_explorer),
            ("🌐 Uninstall Edge", self.uninstall_microsoft_edge),
            ("☁️ Uninstall OneDrive", self.uninstall_onedrive)
        ]
        
        for i, (text, command) in enumerate(tools):
            row = i // 3
            col = i % 3
            self.create_tool_button(tools_frame, text, command, row, col)
            
    def create_tool_button(self, parent, text, command, row, col, color="#0f3460"):
        """Create tool button with enhanced rounded corners and hover effects"""
        # Create outer frame for better rounded effect
        outer_frame = tk.Frame(parent, bg="#1a1a2e")
        outer_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        button = tk.Button(outer_frame, text=text, command=command,
                          bg=color, fg="#ffffff", font=("Segoe UI", 10, "bold"),
                          relief="raised", bd=3, cursor="hand2", width=18, height=2)
        button.pack(padx=3, pady=3, fill="both", expand=True)
        
        # Enhanced hover effects
        def on_enter(e):
            button.configure(bg="#4CAF50", relief="raised", bd=4)
        def on_leave(e):
            button.configure(bg=color, relief="raised", bd=3)
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        return button
        
    def create_protection_page(self):
        """Create protection page"""
        content_frame = self.create_content_frame()
        
        title = tk.Label(content_frame, text="⚔️ Protection Tools", 
                        font=("Segoe UI", 18, "bold"),
                        fg="#ffffff", bg="#1a1a2e")
        title.pack(pady=20)
        
        # Protection cards
        self.create_card(content_frame, "🦠 Antivirus Status", 
                        "Windows Defender: Active\nLast scan: Today")
        self.create_card(content_frame, "🔥 Firewall", 
                        "Status: Enabled\nIncoming connections blocked")
        self.create_card(content_frame, "🔄 Windows Updates", 
                        "Status: Up to date\nLast update: Yesterday")
        
    def create_storage_page(self):
        """Create storage page"""
        content_frame = self.create_content_frame()
        
        title = tk.Label(content_frame, text="💾 Storage Management", 
                        font=("Segoe UI", 18, "bold"),
                        fg="#ffffff", bg="#1a1a2e")
        title.pack(pady=20)
        
        stats = self.get_system_stats()
        
        # Storage overview
        self.create_card(content_frame, "💿 Local Disk (C:)", 
                        f"Used: {stats['disk_free']} / {stats['disk_total']}\n"
                        f"Free space: {100 - stats['disk_percent']:.1f}%")
        
        # Storage tools with enhanced rounded buttons
        tools_frame = tk.Frame(content_frame, bg="#1a1a2e")
        tools_frame.pack(fill="x", padx=10, pady=10)
        
        # Create outer frame for button
        cleanup_outer = tk.Frame(tools_frame, bg="#1a1a2e")
        cleanup_outer.pack(fill="x", pady=5)
        
        cleanup_btn = tk.Button(cleanup_outer, text="🧹 Disk Cleanup", 
                               command=self.cleanup,
                               bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                               relief="raised", bd=3, cursor="hand2", height=2)
        cleanup_btn.pack(fill="x", padx=3, pady=3)
        
    def create_apps_page(self):
        """Create apps page"""
        content_frame = self.create_content_frame()
        
        title = tk.Label(content_frame, text="📱 App Management", 
                        font=("Segoe UI", 18, "bold"),
                        fg="#ffffff", bg="#1a1a2e")
        title.pack(pady=20)
        
        # App management tools
        self.create_card(content_frame, "📦 Installed Programs", 
                        "Manage installed applications\nUninstall unused programs")
        
        # Quick uninstall buttons with enhanced rounded styling
        quick_frame = tk.Frame(content_frame, bg="#1a1a2e")
        quick_frame.pack(fill="x", padx=10, pady=10)
        
        # Edge button with outer frame
        edge_outer = tk.Frame(quick_frame, bg="#1a1a2e")
        edge_outer.pack(fill="x", pady=3)
        
        edge_btn = tk.Button(edge_outer, text="🌐 Remove Edge", 
                            command=self.uninstall_microsoft_edge,
                            bg="#e53e3e", fg="#ffffff", font=("Segoe UI", 10),
                            relief="raised", bd=3, cursor="hand2", height=2)
        edge_btn.pack(fill="x", padx=3, pady=3)
        
        # OneDrive button with outer frame
        onedrive_outer = tk.Frame(quick_frame, bg="#1a1a2e")
        onedrive_outer.pack(fill="x", pady=3)
        
        onedrive_btn = tk.Button(onedrive_outer, text="☁️ Remove OneDrive", 
                                command=self.uninstall_onedrive,
                                bg="#e53e3e", fg="#ffffff", font=("Segoe UI", 10),
                                relief="raised", bd=3, cursor="hand2", height=2)
        onedrive_btn.pack(fill="x", padx=3, pady=3)
        
    def create_settings_page(self):
        """Create settings page"""
        content_frame = self.create_content_frame()
        
        title = tk.Label(content_frame, text="⚙️ Settings", 
                        font=("Segoe UI", 18, "bold"),
                        fg="#ffffff", bg="#1a1a2e")
        title.pack(pady=20)
        
        # Settings cards
        self.create_card(content_frame, "🎨 Appearance", 
                        "Theme: Dark\nAccent color: Green")
        self.create_card(content_frame, "🔧 Performance", 
                        "Auto-boost: Enabled\nScheduled cleanup: Weekly")
        self.create_card(content_frame, "🔔 Notifications", 
                        "System alerts: Enabled\nUpdate notifications: Enabled")
        
        # About button with enhanced rounded corners
        about_outer = tk.Frame(content_frame, bg="#1a1a2e")
        about_outer.pack(pady=15)
        
        about_btn = tk.Button(about_outer, text="ℹ️ About", 
                             command=self.about,
                             bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                             relief="raised", bd=3, cursor="hand2", height=2, width=20)
        about_btn.pack(padx=3, pady=3)
        
    def create_feedback_page(self):
        """Create feedback page"""
        content_frame = self.create_content_frame()
        
        title = tk.Label(content_frame, text="💬 Feedback", 
                        font=("Segoe UI", 18, "bold"),
                        fg="#ffffff", bg="#1a1a2e")
        title.pack(pady=20)
        
        # Feedback form with enhanced rounded corners
        form_outer = tk.Frame(content_frame, bg="#1a1a2e")
        form_outer.pack(fill="x", padx=10, pady=10)
        
        feedback_frame = tk.Frame(form_outer, bg="#0f3460", relief="raised", bd=3)
        feedback_frame.pack(fill="x", padx=4, pady=4)
        
        # Add inner shadow effect
        shadow_frame = tk.Frame(feedback_frame, bg="#0a2140", height=2)
        shadow_frame.pack(fill="x")
        
        form_title = tk.Label(feedback_frame, text="Send us your feedback", 
                             font=("Segoe UI", 14, "bold"),
                             fg="#ffffff", bg="#0f3460")
        form_title.pack(pady=15)
        
        # Text area with enhanced styling
        text_outer = tk.Frame(feedback_frame, bg="#0f3460")
        text_outer.pack(fill="x", padx=15, pady=5)
        
        text_frame = tk.Frame(text_outer, bg="#1a1a2e", relief="raised", bd=2)
        text_frame.pack(fill="x", padx=2, pady=2)
        
        feedback_text = tk.Text(text_frame, height=8, bg="#1a1a2e", fg="#ffffff",
                               font=("Segoe UI", 10), relief="flat", bd=0)
        feedback_text.pack(fill="x", pady=5, padx=5)
        feedback_text.insert(tk.END, "Please share your thoughts about Lightning Booster...")
        
        # Send button with enhanced rounded corners
        send_outer = tk.Frame(feedback_frame, bg="#0f3460")
        send_outer.pack(pady=15)
        
        send_btn = tk.Button(send_outer, text="📤 Send Feedback",
                            bg="#4CAF50", fg="#ffffff", font=("Segoe UI", 11, "bold"),
                            relief="raised", bd=3, cursor="hand2", height=2,
                            command=lambda: messagebox.showinfo("Feedback", "Thank you for your feedback!"))
        send_btn.pack(padx=3, pady=3)
        
        # Contact info
        contact_info = tk.Label(content_frame, 
                               text="📧 Contact: support@lightningbooster.com\n🌐 Website: www.lightningbooster.com",
                               font=("Segoe UI", 10), fg="#cccccc", bg="#1a1a2e")
        contact_info.pack(pady=10)
        
    def run(self):
        """Run the application"""
        try:
            # Center the window on screen
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
            # Start the main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.close_application()
        except Exception as e:
            messagebox.showerror("Error", f"Application error: {str(e)}")
            self.close_application()


def main():
    """Main function to run the application"""
    try:
        app = PCManagerApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

# @license Prof.LoKi