import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import psutil
import cpuinfo
import sv_ttk
import multiprocessing

class AdvancedCpuTool(tb.Window):
    def __init__(self):
        super().__init__(themename="darkly")
        self.title("Advanced CPU Information Tool")
        self.geometry("700x650")
        self.resizable(False, False)

        sv_ttk.set_theme("dark")

        container = tb.Frame(self, padding=15)
        container.pack(fill=BOTH, expand=YES)

        title_label = tb.Label(
            container,
            text="CPU System Information",
            font=("Helvetica", 20, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))

        self.notebook = tb.Notebook(container)
        self.notebook.pack(fill=BOTH, expand=YES)

        self.create_specs_tab()
        self.create_usage_tab()

    def create_specs_tab(self):
        """Creates the tab with detailed CPU specifications."""
        specs_frame = tb.Frame(self.notebook, padding=10)
        self.notebook.add(specs_frame, text=" CPU Specifications ")

        info_text = ScrolledText(specs_frame, wrap=tk.WORD, font=("Consolas", 10), relief="flat")
        info_text.pack(fill=BOTH, expand=YES)

        cpu_data = self.get_detailed_cpu_info()

        info_text.insert(END, f"{'Processor:'.ljust(25)} {cpu_data.get('brand_raw', 'N/A')}\n")
        info_text.insert(END, f"{'Architecture:'.ljust(25)} {cpu_data.get('arch_string_raw', 'N/A')}\n")
        info_text.insert(END, f"{'Bits:'.ljust(25)} {cpu_data.get('bits', 'N/A')}-bit\n")
        info_text.insert(END, "-"*60 + "\n\n")

        info_text.insert(END, f"{'Physical Cores:'.ljust(25)} {cpu_data.get('physical_cores', 'N/A')}\n")
        info_text.insert(END, f"{'Logical Processors:'.ljust(25)} {cpu_data.get('logical_processors', 'N/A')}\n")
        info_text.insert(END, "-"*60 + "\n\n")

        info_text.insert(END, f"{'Max Frequency:'.ljust(25)} {cpu_data.get('max_freq', 0.0):.2f} MHz\n")
        info_text.insert(END, f"{'Min Frequency:'.ljust(25)} {cpu_data.get('min_freq', 0.0):.2f} MHz\n")
        info_text.insert(END, "-"*60 + "\n\n")

        info_text.insert(END, f"{'L1 Data Cache Size:'.ljust(25)} {cpu_data.get('l1_data_cache_size', 'N/A')}\n")
        info_text.insert(END, f"{'L1 Instruction Cache Size:'.ljust(25)} {cpu_data.get('l1_instruction_cache_size', 'N/A')}\n")
        info_text.insert(END, f"{'L2 Cache Size:'.ljust(25)} {cpu_data.get('l2_cache_size', 'N/A')}\n")
        info_text.insert(END, f"{'L3 Cache Size:'.ljust(25)} {cpu_data.get('l3_cache_size', 'N/A')}\n")
        info_text.insert(END, "-"*60 + "\n\n")

        info_text.insert(END, "Instruction Sets (Flags):\n")
        flags = cpu_data.get('flags', [])
        flags_line = ", ".join(flag.upper() for flag in flags)
        info_text.insert(END, flags_line + "\n")

        info_text.config(state="disabled")

    def create_usage_tab(self):
        """Creates the tab for real-time CPU usage monitoring."""
        usage_frame = tb.Frame(self.notebook, padding=10)
        self.notebook.add(usage_frame, text=" Live Usage ")

        total_usage_frame = tb.Frame(usage_frame)
        total_usage_frame.pack(fill=X, pady=10)
        tb.Label(total_usage_frame, text="Total CPU Usage:", font=("Helvetica", 12)).pack(side=LEFT, padx=(0, 10))
        self.total_usage_bar = tb.Progressbar(total_usage_frame, bootstyle="success-striped", length=300)
        self.total_usage_bar.pack(side=LEFT, fill=X, expand=YES)
        self.total_usage_label = tb.Label(total_usage_frame, text="  0%", font=("Helvetica", 12, "bold"))
        self.total_usage_label.pack(side=LEFT, padx=(10, 0))

        tb.Separator(usage_frame).pack(fill=X, pady=15)
        tb.Label(usage_frame, text="Per-Core Usage", font=("Helvetica", 14, "bold")).pack(pady=(0, 10))

        cores_frame = tb.Frame(usage_frame)
        cores_frame.pack(fill=BOTH, expand=YES)

        self.core_bars = []
        self.core_labels = []
        num_cores = psutil.cpu_count(logical=True)
        num_cols = 2
        for i in range(num_cores):
            row, col = divmod(i, num_cols)
            core_frame = tb.Frame(cores_frame)
            core_frame.grid(row=row, column=col, padx=20, pady=5, sticky="ew")

            tb.Label(core_frame, text=f"Core {i+1}:").pack(side=LEFT)
            bar = tb.Progressbar(core_frame, bootstyle="info-striped", length=150)
            bar.pack(side=LEFT, fill=X, expand=YES, padx=5)
            label = tb.Label(core_frame, text="0%", width=5)
            label.pack(side=LEFT)
            self.core_bars.append(bar)
            self.core_labels.append(label)

        cores_frame.grid_columnconfigure(0, weight=1)
        cores_frame.grid_columnconfigure(1, weight=1)

        self.update_usage()

    def get_detailed_cpu_info(self):
        """Gathers comprehensive CPU data from multiple libraries."""
        info = cpuinfo.get_cpu_info()
        psutil_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_processors": psutil.cpu_count(logical=True),
        }
        try:
            freq = psutil.cpu_freq()
            psutil_info["max_freq"] = freq.max
            psutil_info["min_freq"] = freq.min
        except Exception:
            psutil_info["max_freq"] = 0.0
            psutil_info["min_freq"] = 0.0

        info.update(psutil_info)
        
        def format_bytes(size_in_bytes):
            if size_in_bytes is None or size_in_bytes == 0:
                return "N/A"
            power = 1024
            n = 0
            power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
            while size_in_bytes >= power and n < len(power_labels):
                size_in_bytes /= power
                n += 1
            return f"{size_in_bytes:.0f} {power_labels[n]}B"

        info['l2_cache_size'] = format_bytes(info.get('l2_cache_size', 0))
        info['l3_cache_size'] = format_bytes(info.get('l3_cache_size', 0))
        info['l1_data_cache_size'] = format_bytes(info.get('l1_data_cache_size', 0))
        info['l1_instruction_cache_size'] = format_bytes(info.get('l1_instruction_cache_size', 0))
        
        return info

    def update_usage(self):
        """Periodically updates the CPU usage bars and labels."""
        total_percent = psutil.cpu_percent(interval=None)
        self.total_usage_bar['value'] = total_percent
        self.total_usage_label.config(text=f" {total_percent: >3.0f}%")

        core_percents = psutil.cpu_percent(percpu=True)
        for i, percent in enumerate(core_percents):
            self.core_bars[i]['value'] = percent
            self.core_labels[i].config(text=f"{percent: >3.0f}%")

        self.after(1000, self.update_usage)

if __name__ == "__main__":
    multiprocessing.freeze_support()

    app = AdvancedCpuTool()
    app.mainloop()