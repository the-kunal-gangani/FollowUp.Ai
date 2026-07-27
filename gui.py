import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import csv
from pathlib import Path

from transcriber import transcribe_audio
from extractor import extract_action_items, check_ollama_available, check_groq_available
from settings import load_settings, save_settings

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PRIORITY_COLORS = {
    "High": "#FC8181",
    "Medium": "#F6E05E",
    "Low": "#68D391",
}

WHISPER_MODEL_SIZES = ["tiny", "base", "small", "medium"]
OLLAMA_MODELS = ["llama3.2", "phi3", "mistral", "gemma2"]
GROQ_MODELS = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_saved=None):
        super().__init__(parent)
        self.on_saved = on_saved
        self.title("Settings")
        self.geometry("480x520")
        self.transient(parent)
        self.grab_set()

        self.settings = load_settings()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container, text="Extraction Backend", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            container, text="Local: free, private, needs your PC to run the model.\n"
                             "Cloud (Groq): free tier, faster, needs an internet connection + API key.",
            font=ctk.CTkFont(size=10), text_color="#718096", justify="left"
        ).pack(anchor="w", pady=(0, 8))

        self.backend_switch = ctk.CTkSegmentedButton(
            container, values=["local", "cloud"], command=self._on_backend_changed
        )
        self.backend_switch.set(self.settings.get("extraction_backend", "local"))
        self.backend_switch.pack(fill="x", pady=(0, 16))

        self.local_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.cloud_frame = ctk.CTkFrame(container, fg_color="transparent")

        self._build_local_frame()
        self._build_cloud_frame()

        self.whisper_label = ctk.CTkLabel(
            container, text="Whisper Model Size (audio transcription)",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.whisper_label.pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(
            container, text="Larger = more accurate, but slower and bigger download",
            font=ctk.CTkFont(size=10), text_color="#718096"
        ).pack(anchor="w", pady=(0, 4))
        self.whisper_menu = ctk.CTkOptionMenu(container, values=WHISPER_MODEL_SIZES)
        self.whisper_menu.set(self.settings.get("whisper_model_size", "base"))
        self.whisper_menu.pack(fill="x", pady=(4, 20))

        ctk.CTkButton(
            container, text="Save", height=40, fg_color="#2F855A", hover_color="#276749",
            command=self._save
        ).pack(fill="x")

        self._show_backend_frame(self.settings.get("extraction_backend", "local"))

    def _build_local_frame(self):
        ctk.CTkLabel(
            self.local_frame, text="Ollama Host", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")
        self.host_entry = ctk.CTkEntry(self.local_frame, height=38)
        self.host_entry.pack(fill="x", pady=(4, 4))
        self.host_entry.insert(0, self.settings.get("ollama_host", "http://localhost:11434"))

        ctk.CTkLabel(
            self.local_frame, text="Requires the Ollama app running locally (ollama.com)",
            font=ctk.CTkFont(size=10), text_color="#718096"
        ).pack(anchor="w", pady=(0, 10))

        test_row = ctk.CTkFrame(self.local_frame, fg_color="transparent")
        test_row.pack(fill="x", pady=(0, 14))
        self.local_test_label = ctk.CTkLabel(
            test_row, text="", font=ctk.CTkFont(size=11), text_color="#A0AEC0"
        )
        self.local_test_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            test_row, text="Test Connection", width=130, height=30, fg_color="#2D3748",
            hover_color="#4A5568", command=self._test_local_connection
        ).pack(side="right")

        ctk.CTkLabel(
            self.local_frame, text="Ollama Model", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            self.local_frame, text="Must be pulled first, e.g.: ollama pull llama3.2",
            font=ctk.CTkFont(size=10), text_color="#718096"
        ).pack(anchor="w", pady=(0, 4))
        self.model_menu = ctk.CTkOptionMenu(self.local_frame, values=OLLAMA_MODELS)
        self.model_menu.set(self.settings.get("ollama_model", OLLAMA_MODELS[0]))
        self.model_menu.pack(fill="x", pady=(4, 14))

    def _build_cloud_frame(self):
        ctk.CTkLabel(
            self.cloud_frame, text="Groq API Key", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")
        self.groq_key_entry = ctk.CTkEntry(self.cloud_frame, height=38, show="*")
        self.groq_key_entry.pack(fill="x", pady=(4, 4))
        self.groq_key_entry.insert(0, self.settings.get("groq_api_key", ""))

        ctk.CTkLabel(
            self.cloud_frame, text="Free key at console.groq.com/keys",
            font=ctk.CTkFont(size=10), text_color="#718096"
        ).pack(anchor="w", pady=(0, 10))

        test_row = ctk.CTkFrame(self.cloud_frame, fg_color="transparent")
        test_row.pack(fill="x", pady=(0, 14))
        self.cloud_test_label = ctk.CTkLabel(
            test_row, text="", font=ctk.CTkFont(size=11), text_color="#A0AEC0"
        )
        self.cloud_test_label.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            test_row, text="Test Connection", width=130, height=30, fg_color="#2D3748",
            hover_color="#4A5568", command=self._test_cloud_connection
        ).pack(side="right")

        ctk.CTkLabel(
            self.cloud_frame, text="Groq Model", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w")
        self.groq_model_menu = ctk.CTkOptionMenu(self.cloud_frame, values=GROQ_MODELS)
        self.groq_model_menu.set(self.settings.get("groq_model", GROQ_MODELS[0]))
        self.groq_model_menu.pack(fill="x", pady=(4, 14))

    def _on_backend_changed(self, value):
        self._show_backend_frame(value)

    def _show_backend_frame(self, backend):
        self.local_frame.pack_forget()
        self.cloud_frame.pack_forget()
        if backend == "cloud":
            self.cloud_frame.pack(fill="x", before=self.whisper_label)
        else:
            self.local_frame.pack(fill="x", before=self.whisper_label)

    def _test_local_connection(self):
        host = self.host_entry.get().strip()
        available, error = check_ollama_available(host)
        if available:
            self.local_test_label.configure(text="Connected successfully.", text_color="#68D391")
        else:
            self.local_test_label.configure(text="Could not connect.", text_color="#FC8181")

    def _test_cloud_connection(self):
        api_key = self.groq_key_entry.get().strip()
        available, error = check_groq_available(api_key)
        if available:
            self.cloud_test_label.configure(text="Connected successfully.", text_color="#68D391")
        else:
            self.cloud_test_label.configure(text="Could not connect.", text_color="#FC8181")

    def _save(self):
        new_settings = {
            "extraction_backend": self.backend_switch.get(),
            "ollama_host": self.host_entry.get().strip(),
            "ollama_model": self.model_menu.get(),
            "groq_api_key": self.groq_key_entry.get().strip(),
            "groq_model": self.groq_model_menu.get(),
            "whisper_model_size": self.whisper_menu.get(),
        }
        success, error = save_settings(new_settings)
        if not success:
            messagebox.showerror("Save Failed", error)
            return
        if self.on_saved:
            self.on_saved()
        self.destroy()


class MeetingExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Action Extractor")
        self.root.geometry("900x680")
        self.root.minsize(760, 560)

        self.settings = load_settings()
        self.action_items = []
        self.is_busy = False

        self._build_header()
        self._build_input_area()
        self._build_action_row()
        self._build_status_row()
        self._build_results_area()

    def _build_header(self):
        header = ctk.CTkFrame(self.root, fg_color="#1A202C", corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text="Meeting Action Extractor",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="#4FD1C5"
        ).pack(side="left", padx=24, pady=20)

        ctk.CTkButton(
            header, text="⚙ Settings", width=110, height=36, fg_color="#2D3748",
            hover_color="#4A5568", command=self.open_settings
        ).pack(side="right", padx=24)

    def _build_input_area(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(fill="both", expand=False, padx=24, pady=(16, 8))

        row = ctk.CTkFrame(frame, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            row, text="Paste a transcript, or upload an audio file",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            row, text="🎙 Upload Audio", width=150, height=32,
            fg_color="#2B6CB0", hover_color="#2C5282",
            command=self.upload_audio
        ).pack(side="right")

        self.transcript_box = ctk.CTkTextbox(frame, height=200, font=ctk.CTkFont(size=13), wrap="word")
        self.transcript_box.pack(fill="both", expand=True)

    def _build_action_row(self):
        row = ctk.CTkFrame(self.root, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 8))

        self.extract_btn = ctk.CTkButton(
            row, text="✨  Extract Action Items", height=44, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2F855A", hover_color="#276749",
            command=self.run_extraction
        )
        self.extract_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.export_btn = ctk.CTkButton(
            row, text="⬇ Export CSV", height=44, width=140, corner_radius=10,
            fg_color="#2D3748", hover_color="#4A5568",
            command=self.export_csv
        )
        self.export_btn.pack(side="left")

    def _build_status_row(self):
        self.status_label = ctk.CTkLabel(
            self.root, text="Paste a transcript or upload audio to begin.",
            font=ctk.CTkFont(size=12), text_color="#A0AEC0"
        )
        self.status_label.pack(fill="x", padx=24, pady=(0, 8))

    def _build_results_area(self):
        self.results_frame = ctk.CTkScrollableFrame(self.root, fg_color="#171923", corner_radius=12)
        self.results_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def open_settings(self):
        SettingsWindow(self.root, on_saved=self._reload_settings)

    def _reload_settings(self):
        self.settings = load_settings()
        self.status_label.configure(text="Settings saved.", text_color="#68D391")

    def upload_audio(self):
        path = filedialog.askopenfilename(
            title="Select an audio file",
            filetypes=[("Audio files", "*.mp3 *.wav *.m4a *.ogg *.flac"), ("All files", "*.*")]
        )
        if not path:
            return
        self._transcribe_in_thread(path)

    def _transcribe_in_thread(self, audio_path):
        self._set_busy(True)
        self.status_label.configure(
            text="Loading Whisper model (first run downloads it, can take a few minutes)...",
            text_color="#F6AD55"
        )

        def worker():
            def report_progress(current_seconds, total_seconds):
                if total_seconds:
                    pct = min(int((current_seconds / total_seconds) * 100), 100)
                    self.root.after(
                        0, self.status_label.configure,
                        {"text": f"Transcribing... {pct}% ({current_seconds:.0f}s / {total_seconds:.0f}s of audio)",
                         "text_color": "#F6AD55"}
                    )

            try:
                text, language = transcribe_audio(
                    audio_path,
                    model_size=self.settings.get("whisper_model_size", "base"),
                    progress_callback=report_progress,
                )
                self.root.after(0, self._on_transcribed, text, language, None)
            except Exception as exc:
                self.root.after(0, self._on_transcribed, None, None, str(exc))

        threading.Thread(target=worker, daemon=True).start()

    def _on_transcribed(self, text, language, error):
        self._set_busy(False)
        if error:
            messagebox.showerror("Transcription Failed", error)
            self.status_label.configure(text="Transcription failed.", text_color="#FC8181")
            return

        self.transcript_box.delete("1.0", "end")
        self.transcript_box.insert("1.0", text)
        self.status_label.configure(
            text=f"Transcribed successfully (detected language: {language}).", text_color="#68D391"
        )

    def run_extraction(self):
        transcript = self.transcript_box.get("1.0", "end").strip()

        if not transcript:
            messagebox.showwarning("Nothing to Extract", "Paste a transcript or upload audio first.")
            return

        self._set_busy(True)
        self.status_label.configure(text="Extracting action items...", text_color="#F6AD55")
        self._clear_results()

        def worker():
            items, error = extract_action_items(
                transcript,
                backend=self.settings.get("extraction_backend", "local"),
                ollama_model=self.settings.get("ollama_model", OLLAMA_MODELS[0]),
                ollama_host=self.settings.get("ollama_host", "http://localhost:11434"),
                groq_api_key=self.settings.get("groq_api_key", ""),
                groq_model=self.settings.get("groq_model", GROQ_MODELS[0]),
            )
            self.root.after(0, self._on_extracted, items, error)

        threading.Thread(target=worker, daemon=True).start()

    def _on_extracted(self, items, error):
        self._set_busy(False)
        if error:
            messagebox.showerror("Extraction Failed", error)
            self.status_label.configure(text="Extraction failed.", text_color="#FC8181")
            return

        self.action_items = items
        self._render_results()

        if not items:
            self.status_label.configure(text="No action items found in this transcript.", text_color="#A0AEC0")
        else:
            self.status_label.configure(text=f"Found {len(items)} action item(s).", text_color="#68D391")

    def _clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def _render_results(self):
        self._clear_results()

        if not self.action_items:
            ctk.CTkLabel(
                self.results_frame, text="No action items detected.",
                font=ctk.CTkFont(size=13), text_color="#718096"
            ).pack(pady=20)
            return

        for item in self.action_items:
            card = ctk.CTkFrame(self.results_frame, fg_color="#1A202C", corner_radius=10)
            card.pack(fill="x", padx=8, pady=6)

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=14, pady=(10, 4))

            ctk.CTkLabel(
                top_row, text=item["task"], font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#E2E8F0", anchor="w", wraplength=560, justify="left"
            ).pack(side="left", fill="x", expand=True)

            priority_color = PRIORITY_COLORS.get(item["priority"], "#A0AEC0")
            ctk.CTkLabel(
                top_row, text=item["priority"], font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=priority_color, text_color="#1A202C", corner_radius=10, padx=10, pady=2
            ).pack(side="right")

            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=14, pady=(0, 10))

            ctk.CTkLabel(
                bottom_row, text=f"Owner: {item['owner']}", font=ctk.CTkFont(size=12),
                text_color="#A0AEC0"
            ).pack(side="left")

            ctk.CTkLabel(
                bottom_row, text=f"Deadline: {item['deadline']}", font=ctk.CTkFont(size=12),
                text_color="#A0AEC0"
            ).pack(side="right")

    def export_csv(self):
        if not self.action_items:
            messagebox.showwarning("Nothing to Export", "Extract action items first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="action_items.csv"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["task", "owner", "deadline", "priority"])
                writer.writeheader()
                writer.writerows(self.action_items)
            self.status_label.configure(text=f"Exported to {Path(path).name}.", text_color="#68D391")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    def _set_busy(self, busy):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        self.extract_btn.configure(state=state)


def main():
    root = ctk.CTk()
    MeetingExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()