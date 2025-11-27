#!/usr/bin/env python3
"""Simple Tkinter GUI for translating SRT subtitle files.

Features:
- Select an SRT file to translate
- Choose source and target languages
- Default: German to Spanish (using opus-de-es for speed)
- Support for multiple translation models (NLLB, OPUS-MT)
- Save translated SRT file
- Progress tracking
- Uses batch translation for GPU efficiency

Expected startup warnings (these are normal and can be ignored):
- TensorFlow oneDNN: Informational message about optimizations
- passlib pkg_resources: Transitive dependency from fastapi-users (will be fixed upstream)
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services.translationservice.factory import get_translation_service
from utils.srt_parser import SRTParser

# Language code mappings
LANGUAGES = {
    "German (de)": "de",
    "Spanish (es)": "es",
    "English (en)": "en",
}

# Translation service options
TRANSLATION_SERVICES = {
    "OPUS-MT DE-ES (Fast)": "opus-de-es",
    "OPUS-MT DE-EN (Fast)": "opus-de-en",
    "NLLB-600M (Multilingual)": "nllb-600m",
}


class SRTTranslationApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("LangPlug SRT Translation Tool")
        self.root.geometry("600x300")

        # Translation service instance (lazy loaded)
        self.translation_service = None
        self.selected_file_var = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the user interface"""
        padding = {"padx": 10, "pady": 10}

        # File selection frame
        file_frame = tk.Frame(self.root)
        file_frame.pack(fill="x", **padding)

        tk.Label(file_frame, text="SRT file:").pack(side="left")

        entry = tk.Entry(file_frame, textvariable=self.selected_file_var, width=50)
        entry.pack(side="left", padx=(5, 5))

        browse_btn = tk.Button(file_frame, text="Browse...", command=self._on_browse)
        browse_btn.pack(side="left")

        # Configuration frame
        config_frame = tk.Frame(self.root)
        config_frame.pack(fill="x", **padding)

        # Source language
        tk.Label(config_frame, text="Source Language:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.source_lang_var = tk.StringVar(value="German (de)")
        source_menu = tk.OptionMenu(config_frame, self.source_lang_var, *LANGUAGES.keys())
        source_menu.grid(row=0, column=1, padx=5, pady=5)

        # Target language
        tk.Label(config_frame, text="Target Language:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.target_lang_var = tk.StringVar(value="Spanish (es)")
        target_menu = tk.OptionMenu(config_frame, self.target_lang_var, *LANGUAGES.keys())
        target_menu.grid(row=0, column=3, padx=5, pady=5)

        # Translation service
        tk.Label(config_frame, text="Translation Model:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.service_var = tk.StringVar(value="OPUS-MT DE-ES (Fast)")
        service_menu = tk.OptionMenu(config_frame, self.service_var, *TRANSLATION_SERVICES.keys())
        service_menu.grid(row=1, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        # Action frame
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", **padding)

        translate_btn = tk.Button(
            action_frame,
            text="Translate SRT File",
            command=self._on_translate,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
        )
        translate_btn.pack(pady=10)

        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def _on_browse(self) -> None:
        """Handle browse button click"""
        path = filedialog.askopenfilename(
            title="Select SRT file",
            filetypes=[("SRT files", "*.srt"), ("All files", "*.*")],
        )
        if path:
            self.selected_file_var.set(path)

    def _update_status(self, message: str) -> None:
        """Update status label"""
        self.status_label.config(text=message)
        self.root.update()

    def _get_translation_service(self):
        """Get or create translation service instance"""
        service_name = TRANSLATION_SERVICES[self.service_var.get()]

        # Lazy load on first use
        if self.translation_service is None:
            self._update_status(f"Loading translation model: {service_name}...")
            self.translation_service = get_translation_service(service_name)
            self._update_status("Model loaded successfully!")

        return self.translation_service

    def _on_translate(self) -> None:
        """Handle translate button click"""
        srt_path = self.selected_file_var.get().strip()

        if not srt_path:
            messagebox.showerror("Error", "Please select an SRT file first.")
            return

        if not Path(srt_path).exists():
            messagebox.showerror("Error", f"File not found: {srt_path}")
            return

        # Get language codes
        source_lang = LANGUAGES[self.source_lang_var.get()]
        target_lang = LANGUAGES[self.target_lang_var.get()]

        if source_lang == target_lang:
            messagebox.showerror("Invalid Languages", "Source and target languages must be different.")
            return

        try:
            # Load translation service
            service = self._get_translation_service()

            # Parse SRT file
            self._update_status("Parsing SRT file...")
            parser = SRTParser()
            segments = parser.parse_file(srt_path)

            if not segments:
                messagebox.showerror("Error", "No subtitles found in SRT file.")
                return

            self._update_status(f"Translating {len(segments)} subtitles (batched for efficiency)...")

            # Extract texts to translate
            texts_to_translate = [segment.text for segment in segments]

            # Batch translate all texts at once (much faster on GPU)
            translation_results = service.translate_batch(texts_to_translate, source_lang, target_lang)

            # Create translated segments
            translated_segments = []
            for segment, result in zip(segments, translation_results, strict=False):
                translated_segment = type(segment)(
                    index=segment.index,
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    text=result.translated_text,
                )
                translated_segments.append(translated_segment)

            # Save translated SRT
            output_path = str(srt_path).replace(".srt", f"_translated_{target_lang}.srt")
            self._update_status("Saving translated SRT file...")

            SRTParser.save_segments(translated_segments, output_path)

            self._update_status("Translation complete!")

            # Show success message
            messagebox.showinfo(
                "Success",
                f"Translation complete!\n\n"
                f"Subtitles translated: {len(segments)}\n"
                f"Source: {source_lang}\n"
                f"Target: {target_lang}\n\n"
                f"Saved to:\n{output_path}",
            )

        except Exception as exc:
            messagebox.showerror("Translation Failed", f"Error during translation:\n{exc}")
            self._update_status(f"Error: {exc}")

    def run(self) -> None:
        """Run the application"""
        self.root.mainloop()


def main() -> None:
    app = SRTTranslationApp()
    app.run()


if __name__ == "__main__":
    main()
