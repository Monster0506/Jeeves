"""
Chat display component for Jeeves GUI.
"""

import logging
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from typing import Callable, List, Optional

import customtkinter as ctk
from markdown_it import MarkdownIt
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin

from ..config.settings import APP_SETTINGS, COLORS

logger = logging.getLogger(__name__)
logging.getLogger("markdown_it").setLevel(logging.WARNING)


class MessageBubble(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        sender,
        message,
        timestamp,
        is_user,
        theme,
        font_family,
        max_width=600,
        **kwargs,
    ):
        super().__init__(parent, fg_color=theme["bg_chat"], corner_radius=20, **kwargs)
        self.theme = theme
        self.is_user = is_user
        self.font_family = font_family
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.max_width = max_width
        self._bubble = None
        self._msg_frame = None
        self._link_counter = 0
        self._footnote_anchors = {}
        self._build_bubble(sender, message, timestamp)

    def _build_bubble(self, sender, message, timestamp):
        if self._bubble:
            self._bubble.destroy()
        # Bubble color and alignment
        bubble_color = self.theme["bubble_user"] if self.is_user else self.theme["bubble_ai"]
        bubble_hover_color = self.theme["bubble_user_hover"] if self.is_user else self.theme["bubble_ai_hover"]
        text_color = self.theme["text_primary"]
        anchor = "e" if self.is_user else "w"
        padx = (16, 16)
        # Bubble frame with enhanced styling
        self._bubble = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            corner_radius=24,  # Increased for modern look
            border_width=2,  # Increased for better definition
            border_color=self.theme.get("border_secondary", self.theme["bg_chat"]),
        )
        self._bubble.grid(row=0, column=0, sticky=anchor, padx=padx, pady=2)
        self._bubble.grid_columnconfigure(0, weight=1)

        # Add hover effect
        def on_enter(event):
            self._bubble.configure(fg_color=bubble_hover_color)

        def on_leave(event):
            self._bubble.configure(fg_color=bubble_color)

        self._bubble.bind("<Enter>", on_enter)
        self._bubble.bind("<Leave>", on_leave)

        # Sender/timestamp with improved styling
        meta_frame = ctk.CTkFrame(self._bubble, fg_color=bubble_color)
        meta_frame.grid(row=0, column=0, sticky="w", padx=16, pady=(8, 0))
        sender_label = ctk.CTkLabel(
            meta_frame,
            text=sender,
            font=(self.font_family, 12, "bold"),
            text_color=text_color,
        )
        sender_label.pack(side="left")
        time_label = ctk.CTkLabel(
            meta_frame,
            text=timestamp,
            font=(self.font_family, 10),
            text_color=self.theme["text_secondary"],
        )
        time_label.pack(side="left", padx=(8, 0))
        # Markdown message
        if self._msg_frame:
            self._msg_frame.destroy()
        self._msg_frame = ctk.CTkFrame(self._bubble, fg_color=bubble_color)
        self._msg_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=(2, 8))
        self._msg_frame.grid_columnconfigure(0, weight=1)
        self._render_markdown(self._msg_frame, message, text_color)
        # Set max width
        self._msg_frame.update_idletasks()
        width = min(max(self._msg_frame.winfo_reqwidth(), 320), self.max_width)
        self._bubble.configure(width=width)

    def update_max_width(self, max_width):
        self.max_width = max_width
        self._msg_frame.configure(width=max_width - 24)  # Update wraplength container
        # No need to rebuild the whole bubble, just update wraplength if possible
        # For now, let's see if we can avoid rebuilding. With CTkTextbox, wrap is handled.

    def destroy(self):
        """Properly destroy the message bubble and its internal widgets."""
        try:
            # Clean up internal widgets
            if hasattr(self, "_bubble") and self._bubble:
                try:
                    self._bubble.destroy()
                except tk.TclError as e:
                    logger.debug(f"Widget already destroyed: {e}")
                except Exception as e:
                    logger.warning(f"Error destroying bubble widget: {e}")
                self._bubble = None

            if hasattr(self, "_msg_frame") and self._msg_frame:
                try:
                    self._msg_frame.destroy()
                except tk.TclError as e:
                    logger.debug(f"Widget already destroyed: {e}")
                except Exception as e:
                    logger.warning(f"Error destroying message frame: {e}")
                self._msg_frame = None

            # Call parent destroy
            super().destroy()
        except tk.TclError as e:
            logger.debug(f"Parent widget already destroyed: {e}")
        except Exception as e:
            logger.warning(f"Error during widget destruction: {e}")

    def _render_markdown(self, parent, text, text_color):
        # Use a Textbox for better markdown rendering with styles
        md_text = ctk.CTkTextbox(
            parent,
            fg_color=(self.theme["bubble_ai"] if not self.is_user else self.theme["bubble_user"]),
            text_color=text_color,
            font=(self.font_family, 13),
            wrap="word",
            activate_scrollbars=False,
            padx=0,
            pady=0,
            spacing1=0,
            spacing2=5,
            spacing3=5,
            border_width=0,
            width=self.max_width - 32,  # account for padding (16px * 2)
        )
        md_text.grid(row=0, column=0, sticky="ew")

        # Configure tags for markdown styling
        md_text.tag_config("h1", spacing1=10, spacing3=10)
        md_text.tag_config("h2", spacing1=8, spacing3=8)
        md_text.tag_config("h3", spacing1=5, spacing3=5)
        # md_text.tag_config("bold") # No visual change without font
        # md_text.tag_config("italic") # No visual change without font

        md_text.tag_config(
            "code_inline",
            background=self.theme.get("bg_tertiary", "#23272F"),
            foreground=self.theme.get("accent_primary", "#3b82f6"),
            rmargin=4,
            lmargin1=4,
            lmargin2=4,
        )
        md_text.tag_config(
            "code_block",
            background=self.theme.get("bg_tertiary", "#23272F"),
            foreground=self.theme.get("accent_primary", "#3b82f6"),
            lmargin1=10,
            lmargin2=10,
            rmargin=10,
            spacing1=8,
            spacing3=8,
        )

        md_text.tag_config(
            "blockquote",
            lmargin1=20,
            lmargin2=20,
            foreground=self.theme["text_secondary"],
        )
        md_text.tag_config("link", foreground=self.theme.get("link", "royal blue"), underline=True)
        md_text.tag_config(
            "link_hover",
            foreground=self.theme.get("link_hover", "light blue"),
            underline=True,
        )
        md_text.tag_config(
            "footnote_ref",
            foreground=self.theme.get("link", "royal blue"),
            underline=True,
        )

        md_text.tag_config(
            "math_inline",
            background=self.theme.get("bg_tertiary", "#343A40"),
            foreground=self.theme.get("text_primary", "#E9ECEF"),
            rmargin=4,
            lmargin1=4,
            lmargin2=4,
        )
        md_text.tag_config(
            "math_block",
            background=self.theme.get("bg_tertiary", "#343A40"),
            foreground=self.theme.get("text_primary", "#E9ECEF"),
            lmargin1=10,
            lmargin2=10,
            rmargin=10,
            spacing1=8,
            spacing3=8,
        )

        md_text.tag_config(
            "footnote_anchor",
            lmargin1=20,
            lmargin2=20,
            foreground=self.theme["text_secondary"],
        )
        md_text.tag_config(
            "math_inline",
            background="#343A40",
            foreground="#E9ECEF",
            rmargin=4,
            lmargin1=4,
            lmargin2=4,
        )
        md_text.tag_config(
            "math_block",
            background="#343A40",
            foreground="#E9ECEF",
            lmargin1=10,
            lmargin2=10,
            rmargin=10,
            spacing1=8,
            spacing3=8,
        )

        md = MarkdownIt("gfm-like").enable("table").use(footnote_plugin).use(deflist_plugin).use(dollarmath_plugin)
        tokens = md.parse(text)

        def open_link(url):
            try:
                webbrowser.open(url, new=2)
            except Exception as e:
                logger.error(f"Failed to open link {url}: {e}")

        def scroll_to_footnote(footnote_id):
            anchor_tag = f"fn-anchor-{footnote_id}"
            if anchor_tag in md_text.tag_names():
                md_text._textbox.see(f"{anchor_tag}.first")

        tag_stack = []

        def apply_tags(content, token_tags):
            all_tags = tag_stack + token_tags
            md_text.insert("end", content, tuple(all_tags))

        def _render_table_to_text(table_tokens):
            header = []
            rows = []
            current_row = []
            in_header = False

            for i, token in enumerate(table_tokens):
                if token.type == "thead_open":
                    in_header = True
                elif token.type == "thead_close":
                    in_header = False
                elif token.type == "tr_open":
                    current_row = []
                elif token.type == "tr_close":
                    if in_header:
                        header = current_row
                    else:
                        rows.append(current_row)
                elif token.type == "inline":
                    current_row.append(token.content.strip())

            if not header and not rows:
                return ""
            num_cols = len(header) if header else (len(rows[0]) if rows else 0)
            if num_cols == 0:
                return ""
            col_widths = [0] * num_cols

            while len(header) < num_cols:
                header.append("")
            for i in range(num_cols):
                col_widths[i] = len(header[i])

            for row in rows:
                while len(row) < num_cols:
                    row.append("")
                for i in range(num_cols):
                    col_widths[i] = max(col_widths[i], len(row[i]))

            def format_row(row_data, widths, is_header=False):
                return " | ".join(f"{cell:<{widths[i]}}" for i, cell in enumerate(row_data))

            output = []
            if header:
                output.append(format_row(header, col_widths, is_header=True))
                output.append("-|-".join("-" * w for w in col_widths))
            for row in rows:
                output.append(format_row(row, col_widths))

            return "\n".join(output)

        md_text.configure(state="normal")
        md_text.delete("1.0", "end")

        i = 0
        while i < len(tokens):
            token = tokens[i]

            # Handle tables
            if token.type == "table_open":
                table_end_index = -1
                for j in range(i + 1, len(tokens)):
                    if tokens[j].type == "table_close":
                        table_end_index = j
                        break

                if table_end_index != -1:
                    table_tokens = tokens[i + 1 : table_end_index]
                    table_text = _render_table_to_text(table_tokens)
                    if table_text:
                        apply_tags(table_text + "\n", ["code_block"])
                    i = table_end_index
                i += 1
                continue

            if token.type.endswith("_open"):
                tag = token.tag if token.tag else token.type.split("_")[0]

                if token.type == "list_item_open":
                    tag_stack.append("li")

                    indent = "  " * (len([t for t in tag_stack if t == "li"]) - 1)
                    apply_tags(indent, [])

                    if "ol" in tag_stack:
                        bullet = f"{getattr(token, 'info', '')}. "
                        apply_tags(bullet, [])
                    else:
                        apply_tags("• ", [])

                elif tag:
                    tag_stack.append(tag)

            elif token.type.endswith("_close"):
                if token.type == "list_item_close":
                    while tag_stack and tag_stack[-1] != "li":
                        tag_stack.pop()
                    if tag_stack:
                        tag_stack.pop()  # Pop the 'li'
                elif tag_stack:
                    tag_stack.pop()

                if token.type in [
                    "heading_close",
                    "paragraph_close",
                    "blockquote_close",
                    "footnote_close",
                    "footnote_block_close",
                ]:
                    apply_tags("\n", [])

            elif token.type == "inline" and token.children:
                for child in token.children:
                    if child.type == "link_open":
                        href = child.attrs.get("href", "")
                        link_id = f"link-{self._link_counter}"
                        self._link_counter += 1

                        md_text.tag_bind(link_id, "<Button-1>", lambda e, url=href: open_link(url))
                        md_text.tag_bind(
                            link_id,
                            "<Enter>",
                            lambda e: md_text.configure(cursor="hand2"),
                        )
                        md_text.tag_bind(link_id, "<Leave>", lambda e: md_text.configure(cursor=""))

                        tag_stack.append(link_id)
                        tag_stack.append("link")

                    elif child.type == "link_close":
                        if "link" in tag_stack:
                            tag_stack.pop(tag_stack.index("link"))
                        link_id_to_pop = next((t for t in tag_stack if t.startswith("link-")), None)
                        if link_id_to_pop:
                            tag_stack.pop(tag_stack.index(link_id_to_pop))

                    elif child.type.endswith("_open"):
                        tag = child.tag if child.tag else child.type.split("_")[0]
                        if tag == "em":
                            tag = "italic"
                        if tag == "strong":
                            tag = "bold"
                        tag_stack.append(tag)

                    elif child.type.endswith("_close"):
                        if tag_stack:
                            tag_stack.pop()
                    elif child.type == "text":
                        apply_tags(child.content, [])
                    elif child.type == "code_inline":
                        apply_tags(child.content, ["code_inline"])
                    elif child.type == "softbreak":
                        apply_tags("\n", [])
                    elif child.type == "hardbreak":
                        apply_tags("\n\n", [])
                    elif child.type == "footnote_ref":
                        ref_id = child.meta["id"]
                        fn_id = f"footnote-{ref_id}"
                        md_text.tag_bind(
                            fn_id,
                            "<Button-1>",
                            lambda e, f_id=ref_id: scroll_to_footnote(f_id),
                        )
                        md_text.tag_bind(
                            fn_id,
                            "<Enter>",
                            lambda e: md_text.configure(cursor="hand2"),
                        )
                        md_text.tag_bind(fn_id, "<Leave>", lambda e: md_text.configure(cursor=""))
                        apply_tags(f"[{ref_id}]", ["footnote_ref", fn_id])

            elif token.type == "fence":
                apply_tags(f"{token.content.strip()}\n", ["code_block"])

            elif token.type == "hr":
                apply_tags("─" * 20 + "\n", [])

            elif token.type == "text":
                apply_tags(token.content, [])

            elif token.type == "footnote_anchor":
                anchor_id = token.meta["id"]
                anchor_tag = f"fn-anchor-{anchor_id}"
                apply_tags(f"[{anchor_id}]: ", [anchor_tag])

            elif token.type == "math_inline":
                apply_tags(token.content, ["math_inline"])

            elif token.type == "math_block":
                apply_tags(token.content + "\n", ["math_block"])

            i += 1

        md_text.configure(state="disabled")

        # Auto-adjust height of the textbox
        md_text.update_idletasks()
        try:
            # A bit of a hack to get the used height of the text
            # Use the underlying tkinter Text widget to count displayed lines
            lines = md_text._textbox.count("1.0", "end", "displaylines")[0]

            # Font is a tuple, e.g., ("Fira Code", 12), get size from index 1
            font_tuple = md_text.cget("font")
            font_size = font_tuple[1]

            # Add some padding
            height = lines * (font_size + 9)
            md_text.configure(height=height)
        except (tk.TclError, ValueError, TypeError) as e:
            # If height calculation fails, just leave it, it's not critical
            logger.debug(f"Height calculation failed: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error in height calculation: {e}")


class AttachmentPill(ctk.CTkFrame):
    """A widget to display a single attachment in the input area."""

    def __init__(self, parent, attachment_info: dict, on_remove: Callable):
        super().__init__(parent, fg_color=("#E0E0E0", "#4A4D50"), corner_radius=12)
        self.pack(side="left", padx=4, pady=4)

        # File icon
        icon_label = ctk.CTkLabel(self, text="📄", font=(None, 16))
        icon_label.pack(side="left", padx=(8, 4))

        # File name
        file_name = attachment_info.get("name", "Unknown file")
        name_label = ctk.CTkLabel(self, text=file_name, font=(None, 12))
        name_label.pack(side="left", padx=4)

        # Remove button
        remove_button = ctk.CTkButton(
            self,
            text="✕",
            width=20,
            height=20,
            corner_radius=10,
            fg_color=("#D0D0D0", "#3A3D40"),
            hover_color=("#C0C0C0", "#2A2D30"),
            command=on_remove,
        )
        remove_button.pack(side="left", padx=(4, 8))


class ChatDisplay(ctk.CTkFrame):
    """Modern chat display with bubble design and markdown support."""

    def __init__(
        self,
        parent,
        on_send_message: Optional[Callable] = None,
        on_export_chat: Optional[Callable] = None,
        on_search_messages: Optional[Callable] = None,
        on_attachment: Optional[Callable] = None,
    ):
        super().__init__(parent)
        self.on_send_message = on_send_message
        self.on_export_chat = on_export_chat
        self.on_search_messages = on_search_messages
        self.on_attachment = on_attachment
        self.theme = COLORS["dark"]
        self.font_family = APP_SETTINGS["font_family"]
        self.bubbles = []
        self._current_attachments = []  # Initialize attachments list
        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        # Scrollable chat area with enhanced styling
        self.canvas = tk.Canvas(
            self,
            bg=self.theme["bg_chat"],
            highlightthickness=0,
            borderwidth=0,
            selectbackground=self.theme.get("selection", "#3b82f6"),
        )
        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview,
            bg=self.theme["bg_secondary"],
            troughcolor=self.theme["bg_primary"],
            activebackground=self.theme["accent_primary"],
        )
        self.scrollable_frame = ctk.CTkFrame(self, fg_color=self.theme["bg_chat"])
        self.scrollable_frame.bind("<Configure>", lambda e: self._on_frame_configure())
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Add mouse wheel scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        # Input area with enhanced styling and consistent spacing
        self.input_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=16,  # Increased for modern look
            border_width=2,  # Increased for better definition
            border_color=self.theme["border_primary"],
        )
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(16, 8))  # Consistent spacing, less bottom padding
        self.input_frame.grid_columnconfigure(1, weight=1)  # Changed to column 1 for paperclip button

        # Attachment Tray
        self.attachment_tray = ctk.CTkScrollableFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            height=60,
            orientation="horizontal",
            scrollbar_button_color=self.theme["button_secondary"],
            scrollbar_button_hover_color=self.theme["button_secondary_hover"],
        )
        # This will be gridded later when an attachment is added

        # Paperclip button for file attachments
        self.attachment_button = ctk.CTkButton(
            self.input_frame,
            text="📎",
            command=self._open_file_picker,
            width=48,  # Square button for icon
            height=48,  # Square button for icon
            font=(self.font_family, 16, "bold"),  # Larger font for icon
            fg_color=self.theme["button_secondary"],
            hover_color=self.theme["button_secondary_hover"],
            text_color=self.theme["text_primary"],
            corner_radius=12,  # Increased for modern look
            border_width=1,  # Subtle border for definition
            border_color=self.theme["border_secondary"],
        )
        self.attachment_button.grid(row=0, column=0, padx=(16, 8), pady=16)

        # Initialize input field with proper configuration
        self._create_input_field()

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="➤ Send",  # Added arrow icon for better visual appeal
            command=self._send_message,
            width=104,  # Increased for better proportions with icon
            height=48,  # Increased from 40 for better proportions
            font=(self.font_family, 12, "bold"),  # Made bold for primary action
            fg_color=self.theme["button_primary"],
            hover_color=self.theme["button_primary_hover"],
            text_color=self.theme["text_inverse"],
            corner_radius=12,  # Increased for modern look
            border_width=0,  # Clean look without borders
            # Add subtle shadow effect through color
        )
        self.send_button.grid(row=0, column=2, padx=(8, 16), pady=16)  # Right side of input field

        # Toolbar with enhanced styling and consistent spacing
        self.toolbar_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=12,  # Increased for modern look
            border_width=2,  # Increased for better definition
            border_color=self.theme["border_secondary"],
        )
        self.toolbar_frame.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))  # Consistent spacing, row updated to 3

        self.search_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🔍 Search",
            command=self._search_messages,
            width=120,  # Increased for better proportions
            height=40,  # Increased for better proportions
            font=(self.font_family, 11, "bold"),  # Made bold for better visibility
            fg_color=self.theme["button_secondary"],
            hover_color=self.theme["button_secondary_hover"],
            text_color=self.theme["text_primary"],
            corner_radius=10,  # Increased for modern look
            border_width=1,  # Subtle border for definition
            border_color=self.theme["border_secondary"],
        )
        self.search_button.pack(side="left", padx=16, pady=12)  # Increased padding

        self.export_button = ctk.CTkButton(
            self.toolbar_frame,
            text="📤 Export",
            command=self._export_chat,
            width=120,  # Increased for better proportions
            height=40,  # Increased for better proportions
            font=(self.font_family, 11, "bold"),  # Made bold for better visibility
            fg_color=self.theme["button_secondary"],
            hover_color=self.theme["button_secondary_hover"],
            text_color=self.theme["text_primary"],
            corner_radius=10,  # Increased for modern look
            border_width=1,  # Subtle border for definition
            border_color=self.theme["border_secondary"],
        )
        self.export_button.pack(side="left", padx=(0, 16), pady=12)  # Increased padding

        self.clear_button = ctk.CTkButton(
            self.toolbar_frame,
            text="🗑️ Clear",
            command=self.clear_messages,
            width=120,  # Increased for better proportions
            height=40,  # Increased for better proportions
            font=(self.font_family, 11, "bold"),  # Made bold for better visibility
            fg_color=self.theme["button_danger"],
            hover_color=self.theme["button_danger_hover"],
            text_color=self.theme["text_inverse"],
            corner_radius=10,  # Increased for modern look
            border_width=0,  # No border for danger button
        )
        self.clear_button.pack(side="left", padx=(0, 16), pady=12)  # Increased padding

    def _create_input_field(self):
        """Create the input field with proper configuration."""
        self.input_field = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Type your message here...",
            font=(self.font_family, 13),  # Slightly larger font for better readability
            height=48,  # Increased from 40 for better proportions
            fg_color=self.theme["bg_input"],
            text_color=self.theme["text_primary"],
            placeholder_text_color=self.theme["text_secondary"],
            border_color=self.theme["border_secondary"],
            border_width=1,
            corner_radius=12,  # Increased to match button styling
        )
        self.input_field.grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=16)  # Between paperclip and send button

    def _setup_bindings(self):
        self.input_field.bind("<Return>", lambda e: self._send_message())
        self.input_field.bind("<Shift-Return>", lambda e: self._insert_newline())

        # Add enhanced focus effects to input field
        def on_input_focus_in(event):
            self.input_field.configure(border_color=self.theme["border_focus"])

        def on_input_focus_out(event):
            self.input_field.configure(border_color=self.theme["border_secondary"])

        self.input_field.bind("<FocusIn>", on_input_focus_in)
        self.input_field.bind("<FocusOut>", on_input_focus_out)

        # Add enhanced hover effects to buttons
        self._setup_button_hover_effects()

    def _setup_button_hover_effects(self):
        """Setup enhanced hover effects for buttons."""

        # Send button hover effect
        def on_send_enter(event):
            self.send_button.configure(corner_radius=14)  # Slightly larger radius on hover

        def on_send_leave(event):
            self.send_button.configure(corner_radius=12)  # Return to normal radius

        self.send_button.bind("<Enter>", on_send_enter)
        self.send_button.bind("<Leave>", on_send_leave)

        # Toolbar buttons hover effects
        for button in [self.search_button, self.export_button, self.clear_button]:

            def on_toolbar_enter(event, btn=button):
                btn.configure(corner_radius=12)  # Slightly larger radius on hover

            def on_toolbar_leave(event, btn=button):
                btn.configure(corner_radius=10)  # Return to normal radius

            button.bind("<Enter>", on_toolbar_enter)
            button.bind("<Leave>", on_toolbar_leave)

        # Attachment button hover effect
        def on_attachment_enter(event):
            self.attachment_button.configure(corner_radius=14)  # Slightly larger radius on hover

        def on_attachment_leave(event):
            self.attachment_button.configure(corner_radius=12)  # Return to normal radius

        self.attachment_button.bind("<Enter>", on_attachment_enter)
        self.attachment_button.bind("<Leave>", on_attachment_leave)

    def _send_message(self):
        message = self.input_field.get().strip()

        # Prevent sending empty messages unless there are attachments
        if not message and not self._current_attachments:
            return

        # Extract the attachment info dictionaries from the internal list
        attachments_to_send = [info for key, info, widget in self._current_attachments]

        # The on_send_message callback now receives the pure message text
        # and a list of attachment dictionaries.
        if self.on_send_message:
            self.on_send_message(message, attachments_to_send)

        # Clear the input field and any attachments
        self.input_field.delete(0, "end")
        self._clear_attachments()

    def _insert_newline(self):
        current_text = self.input_field.get()
        cursor_pos = self.input_field.index("insert")
        new_text = current_text[:cursor_pos] + "\n" + current_text[cursor_pos:]
        self.input_field.delete(0, "end")
        self.input_field.insert(0, new_text)
        self.input_field.icursor(cursor_pos + 1)

    def add_user_message(self, message: str):
        self._add_message(message, "You", is_user=True)

    def add_ai_message(self, message: str):
        self._add_message(message, "Jeeves", is_user=False)

    def add_system_message(self, message: str):
        self._add_message(message, "System", is_user=False)

    def _add_message(self, message: str, sender: str, is_user: bool):
        """Add a message with proper error handling to prevent Tkinter errors."""
        try:
            timestamp = datetime.now().strftime("%H:%M")
            max_bubble_width = max(int(self.canvas.winfo_width() * 0.95), 600)

            bubble = MessageBubble(
                self.scrollable_frame,
                sender,
                message,
                timestamp,
                is_user,
                self.theme,
                self.font_family,
                max_width=max_bubble_width,
            )

            if is_user:
                bubble.pack(anchor="e", pady=8, padx=(16, 16), fill=None)
            else:
                bubble.pack(anchor="w", pady=8, padx=(16, 16), fill=None)

            self.bubbles.append(bubble)
            self.update_idletasks()
            self.canvas.yview_moveto(1.0)

        except Exception as e:
            logging.getLogger(__name__).error(f"Error adding message: {e}")
            # Try to continue without the problematic message bubble

    def load_messages(self, messages: List[dict]):
        """Load messages with proper widget cleanup to prevent Tkinter errors."""
        try:
            # Safely destroy existing widgets
            for widget in self.scrollable_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError as e:
                    logger.debug(f"Widget already destroyed: {e}")
                except Exception as e:
                    logger.warning(f"Error destroying widget: {e}")

            self.bubbles.clear()

            for message in messages:
                sender = message.get("sender", "unknown")
                content = message.get("content", "")
                timestamp = message.get("timestamp", "")
                is_user = sender == "user" or sender == "You"
                display_sender = "You" if is_user else ("Jeeves" if sender == "ai" else sender.title())
                max_bubble_width = max(int(self.canvas.winfo_width() * 0.95), 600)

                # Check for attachments and append their info to the content
                if message.get("attachments"):
                    attachment_text = "\n\n**Attachments:**\n"
                    for attachment in message["attachments"]:
                        file_size_mb = attachment.get("file_size", 0) / 1024 / 1024
                        attachment_text += f"- {attachment.get('file_name', '...')} ({file_size_mb:.1f}MB)\n"
                    content += attachment_text

                try:
                    bubble = MessageBubble(
                        self.scrollable_frame,
                        display_sender,
                        content,
                        timestamp,
                        is_user,
                        self.theme,
                        self.font_family,
                        max_width=max_bubble_width,
                    )
                    if is_user:
                        bubble.pack(anchor="e", pady=8, padx=(16, 16), fill=None)
                    else:
                        bubble.pack(anchor="w", pady=8, padx=(16, 16), fill=None)
                    self.bubbles.append(bubble)
                except Exception as e:
                    # Log error but continue loading other messages
                    logger.warning(f"Failed to create message bubble: {e}")
                    continue

            self.update_idletasks()
            self.canvas.yview_moveto(1.0)
        except Exception as e:
            logger.error(f"Error loading messages: {e}")

    def clear_messages(self):
        """Clear messages with proper widget cleanup to prevent Tkinter errors."""
        try:
            # Safely destroy existing widgets
            for widget in self.scrollable_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError as e:
                    logger.debug(f"Widget already destroyed: {e}")
                except Exception as e:
                    logger.warning(f"Error destroying widget: {e}")

            self.bubbles.clear()
            self.update_idletasks()
        except Exception as e:
            logger.error(f"Error clearing messages: {e}")

    def _search_messages(self):
        """Trigger message search."""
        if self.on_search_messages:
            self.on_search_messages()

    def _export_chat(self):
        """Trigger chat export."""
        if self.on_export_chat:
            self.on_export_chat()

    def _on_canvas_resize(self, event):
        """Handle canvas resize with proper error handling."""
        try:
            # Make scrollable_frame always match canvas width
            canvas_items = self.canvas.find_withtag("all")
            if canvas_items:
                self.canvas.itemconfig(canvas_items[0], width=event.width)

            # Update all bubbles' max_width
            max_bubble_width = max(int(event.width * 0.95), 600)
            for bubble in self.bubbles:
                try:
                    bubble.update_max_width(max_bubble_width)
                except tk.TclError as e:
                    logger.debug(f"Bubble widget already destroyed: {e}")
                except Exception as e:
                    logger.warning(f"Error updating bubble max width: {e}")
        except Exception as e:
            logger.warning(f"Error in canvas resize: {e}")

    def _on_frame_configure(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")
        else:  # Windows/Mac
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _open_file_picker(self):
        """Open file picker dialog for attachments."""
        try:
            # Get the sandbox directory from JeevesFileHandler
            from ..core.file_handler import JeevesFileHandler

            file_handler = JeevesFileHandler()
            sandbox_root = file_handler.get_sandbox_root()

            # Open file dialog with common file types
            file_types = [
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("Markdown Files", "*.md"),
                ("JSON Files", "*.json"),
                ("CSV Files", "*.csv"),
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Document Files", "*.pdf *.doc *.docx"),
                ("Code Files", "*.py *.js *.html *.css *.java *.cpp *.c *.h"),
            ]

            file_path = filedialog.askopenfilename(
                title="Select file to attach",
                filetypes=file_types,
                initialdir=sandbox_root,  # Use sandbox directory as default
            )

            if file_path:
                self._handle_file_attachment(file_path)

        except Exception as e:
            logger.error(f"Error opening file picker: {e}")
            # Show error message to user
            self._show_error_message("Failed to open file picker")

    def _handle_file_attachment(self, file_path: str):
        """Handle file attachment processing."""
        try:
            file_path = Path(file_path)

            # Check if file exists
            if not file_path.exists():
                self._show_error_message(f"File not found: {file_path.name}")
                return

            # Check file size (limit to 10MB for now)
            file_size = file_path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10MB

            if file_size > max_size:
                self._show_error_message(f"File too large: {file_path.name} ({file_size / 1024 / 1024:.1f}MB). Maximum size is 10MB.")
                return

            # Get file info
            file_name = file_path.name
            file_extension = file_path.suffix.lower()

            # Create attachment message
            attachment_info = {
                "name": file_name,
                "path": str(file_path),
                "size": file_size,
                "extension": file_extension,
                "type": self._get_file_type(file_extension),
            }

            # Add attachment to the new UI tray
            self._add_attachment(attachment_info)

        except Exception as e:
            logger.error(f"Error handling file attachment: {e}")
            self._show_error_message(f"Failed to process file: {file_path.name}")

    def _get_file_type(self, extension: str) -> str:
        """Get human-readable file type from extension."""
        file_types = {
            ".txt": "Text File",
            ".py": "Python File",
            ".md": "Markdown File",
            ".json": "JSON File",
            ".csv": "CSV File",
            ".png": "Image File",
            ".jpg": "Image File",
            ".jpeg": "Image File",
            ".gif": "Image File",
            ".bmp": "Image File",
            ".pdf": "PDF Document",
            ".doc": "Word Document",
            ".docx": "Word Document",
            ".js": "JavaScript File",
            ".html": "HTML File",
            ".css": "CSS File",
            ".java": "Java File",
            ".cpp": "C++ File",
            ".c": "C File",
            ".h": "Header File",
        }
        return file_types.get(extension, "File")

    def _add_attachment(self, attachment_info: dict):
        """Add a new attachment pill to the UI."""
        # Show the tray if this is the first attachment
        if not self._current_attachments:
            self.attachment_tray.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

        # Use the file path as a unique key
        attachment_key = attachment_info["path"]

        # Prevent duplicate attachments
        if any(key == attachment_key for key, _, _ in self._current_attachments):
            logger.warning(f"Attachment {attachment_info['name']} already added.")
            return

        # Create the pill widget and store a reference to it
        pill = AttachmentPill(
            self.attachment_tray,
            attachment_info,
            lambda: self._remove_attachment(attachment_key),
        )

        # Store attachment info along with its widget
        self._current_attachments.append((attachment_key, attachment_info, pill))

    def _remove_attachment(self, attachment_key: str):
        """Remove an attachment pill from the UI."""
        attachment_to_remove = None
        for attachment in self._current_attachments:
            if attachment[0] == attachment_key:
                attachment_to_remove = attachment
                break

        if attachment_to_remove:
            key, info, pill_widget = attachment_to_remove
            pill_widget.destroy()
            self._current_attachments.remove(attachment_to_remove)
            logger.info(f"Removed attachment: {info['name']}")

        # Hide the tray if no attachments are left
        if not self._current_attachments:
            self.attachment_tray.grid_forget()

    def _show_error_message(self, message: str):
        """Show error message to user."""
        logger.error(f"User error: {message}")
        # You could implement a toast notification system here

    def _clear_attachments(self):
        """Clear all attachment pills."""
        for key, info, pill_widget in self._current_attachments:
            pill_widget.destroy()

        self._current_attachments.clear()
        self.attachment_tray.grid_forget()
        logger.info("Cleared all attachments.")
        # The placeholder is managed by the widget, so no need to configure it here.
