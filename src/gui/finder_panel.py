from typing import Any, Callable

import customtkinter as ctk


class FinderPanel(ctk.CTkFrame):
    """
    A ranger-style finder panel for searching files and chat history.
    """

    def __init__(self, master: Any, on_search: Callable[[str], None]) -> None:
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.on_search = on_search

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.search_entry = ctk.CTkEntry(self, placeholder_text="Search everywhere...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.search_entry.bind("<Return>", self._perform_search)

        self.results_display = ctk.CTkTextbox(self, state="disabled")
        self.results_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _perform_search(self, event: Any) -> None:
        query = self.search_entry.get()
        if query:
            self.on_search(query)

    def show_results(self, results: list[str]) -> None:
        self.results_display.configure(state="normal")
        self.results_display.delete("1.0", "end")
        if results:
            self.results_display.insert("end", "\n".join(results))
        else:
            self.results_display.insert("end", "No results found.")
        self.results_display.configure(state="disabled")

    def show(self) -> None:
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)
        self.search_entry.focus()

    def hide(self) -> None:
        self.place_forget()
