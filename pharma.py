import customtkinter as ctk
import tkinter
from tkinter import ttk, messagebox
from PIL import Image
import mysql.connector
from tkcalendar import DateEntry
import google.generativeai as genai
import threading

class PharmacyManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("1550x800+50+50")
        self.root.minsize(1366, 768)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        self.setup_styles()

        # Initialize all variables
        self.ref_var = ctk.StringVar()
        self.cmpName_var = ctk.StringVar()
        self.medType_var = ctk.StringVar()
        self.medName_var = ctk.StringVar()
        self.lot_var = ctk.StringVar()
        self.issueDate_var = ctk.StringVar()
        self.expDate_var = ctk.StringVar()
        self.uses_var = ctk.StringVar()
        self.sideEffect_var = ctk.StringVar()
        self.warning_var = ctk.StringVar()
        self.dosage_var = ctk.StringVar()
        self.price_var = ctk.StringVar()
        self.product_var = ctk.StringVar()
        self.addmed_var = ctk.StringVar()
        self.refMed_var = ctk.StringVar()
        self.search_combo_var = ctk.StringVar(value="Ref_no")
        self.txtSearch_var = ctk.StringVar()
        self.chat_message_var = ctk.StringVar()

        # Chatbot State Variables
        self.chat_language = 'English'

        self.create_widgets()
        self.fetch_datamed()
        self.fetch_data()
        self.update_medicine_name_list()

    def setup_styles(self):
        style = ttk.Style(self.root)
        bg_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        select_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        header_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])

        style.theme_use("clam")
        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, rowheight=28, font=("Segoe UI", 11))
        style.map("Treeview", background=[('selected', select_color)])
        style.configure("Treeview.Heading", background=header_color, foreground=text_color, relief="flat", font=("Segoe UI", 12, "bold"))
        style.map("Treeview.Heading", background=[('active', select_color)])
        
        style.configure('TCombobox', fieldbackground=bg_color, background=bg_color, foreground=text_color, arrowcolor=text_color,
                        selectbackground=bg_color, selectforeground=text_color, bordercolor=header_color, lightcolor=header_color,
                        darkcolor=header_color, relief='flat')
        style.map('TCombobox', fieldbackground=[('readonly', bg_color)])

    def create_widgets(self):
        title_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        title_frame.pack(side=tkinter.TOP, fill="x")
        lbltitle = ctk.CTkLabel(title_frame, text="PHARMACY MANAGEMENT SYSTEM", font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"))
        lbltitle.pack(pady=18)

        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # === ADJUSTED GRID CONFIGURATION FOR TALLER TOP SECTION ===
        # Changed column weights to give the chat bot more space as requested
        main_frame.grid_columnconfigure(0, weight=2)  # Medicine Info
        main_frame.grid_columnconfigure(1, weight=3)  # AI Chatbot (widest)
        main_frame.grid_columnconfigure(2, weight=2)  # Medicine Dept
        # Give row 0 weight, so it expands vertically
        main_frame.grid_rowconfigure(0, weight=3)     
        main_frame.grid_rowconfigure(3, weight=2)     # Weight for the main table at the bottom

        # Medicine Info Frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew", rowspan=2)
        info_frame_label = ctk.CTkLabel(info_frame, text="Medicine Information", font=ctk.CTkFont(size=16, weight="bold"))
        info_frame_label.grid(row=0, column=0, columnspan=4, pady=10, padx=20, sticky="w")
        form_fields_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        form_fields_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        form_fields_frame.grid_columnconfigure((1, 3), weight=1)
        
        ctk.CTkLabel(form_fields_frame, text="Reference No:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.ref_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Issue Date:").grid(row=0, column=2, sticky="w", padx=10, pady=5)
        DateEntry(form_fields_frame, textvariable=self.issueDate_var, date_pattern='yyyy-mm-dd', font=("Segoe UI", 12)).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Company Name:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.cmpName_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Exp Date:").grid(row=1, column=2, sticky="w", padx=10, pady=5)
        DateEntry(form_fields_frame, textvariable=self.expDate_var, date_pattern='yyyy-mm-dd', font=("Segoe UI", 12)).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Type Of Medicine:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkComboBox(form_fields_frame, variable=self.medType_var, values=["Tablet", "Liquid", "Capsules", "Topical", "Drops", "Inhaler", "Injection"], state="readonly").grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Uses:").grid(row=2, column=2, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.uses_var).grid(row=2, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Medicine Name:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.comMedName = ctk.CTkComboBox(form_fields_frame, variable=self.medName_var, values=[""], state="readonly")
        self.comMedName.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Side Effect:").grid(row=3, column=2, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.sideEffect_var).grid(row=3, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Lot No:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.lot_var).grid(row=4, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Price:").grid(row=4, column=2, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.price_var).grid(row=4, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Dosage:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.dosage_var).grid(row=5, column=1, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Product Qty:").grid(row=5, column=2, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.product_var).grid(row=5, column=3, sticky="ew", padx=5, pady=5)
        ctk.CTkLabel(form_fields_frame, text="Prec & Warning:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        ctk.CTkEntry(form_fields_frame, textvariable=self.warning_var).grid(row=6, column=1, columnspan=3, sticky="ew", padx=5, pady=5)

        # AI Chat Frame
        chat_frame = ctk.CTkFrame(main_frame)
        chat_frame.grid(row=0, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew", rowspan=2)
        chat_frame.grid_rowconfigure(2, weight=1)
        chat_title_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        chat_title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        ctk.CTkLabel(chat_title_frame, text="AI Medical Assistant", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        lang_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        lang_frame.grid(row=1, column=0, sticky="ew", padx=10)
        self.en_button = ctk.CTkButton(lang_frame, text="English", height=25, command=lambda: self.set_language('English'))
        self.en_button.pack(side="left", padx=(0, 5))
        self.hi_button = ctk.CTkButton(lang_frame, text="हिन्दी", height=25, command=lambda: self.set_language('Hindi'))
        self.hi_button.pack(side="left")
        self.set_language('English')
        
        self.chat_display_frame = ctk.CTkScrollableFrame(chat_frame, fg_color=self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]))
        self.chat_display_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        message_frame = ctk.CTkFrame(chat_frame, fg_color="transparent")
        message_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.chat_entry = ctk.CTkEntry(message_frame, textvariable=self.chat_message_var, placeholder_text="Ask about a medicine...")
        self.chat_entry.pack(side="left", expand=True, fill="x", ipady=4)
        self.chat_entry.bind("<Return>", self.send_chat_message)
        send_button = ctk.CTkButton(message_frame, text="Send", width=80, command=self.send_chat_message)
        send_button.pack(side="right", padx=(5, 0))
        self.add_chat_bubble("Hello! How can I help you today?", is_user=False)

        # Medicine Department Frame
        add_dept_frame = ctk.CTkFrame(main_frame)
        add_dept_frame.grid(row=0, column=2, pady=(0, 10), sticky="nsew", rowspan=2)
        add_dept_label = ctk.CTkLabel(add_dept_frame, text="Medicine Department", font=ctk.CTkFont(size=16, weight="bold"))
        add_dept_label.pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(add_dept_frame, text="Ref No:").place(relx=0.1, rely=0.2)
        ctk.CTkEntry(add_dept_frame, textvariable=self.refMed_var).place(relx=0.4, rely=0.2, relwidth=0.5)
        ctk.CTkLabel(add_dept_frame, text="Med Name:").place(relx=0.1, rely=0.3)
        ctk.CTkEntry(add_dept_frame, textvariable=self.addmed_var).place(relx=0.4, rely=0.3, relwidth=0.5)
        med_buttons_frame = ctk.CTkFrame(add_dept_frame, fg_color="transparent")
        med_buttons_frame.place(relx=0.05, rely=0.4, relwidth=0.9, relheight=0.1)
        ctk.CTkButton(med_buttons_frame, text="ADD", command=self.AddMed).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(med_buttons_frame, text="UPDATE", command=self.UpdateMed).pack(side="left", expand=True, padx=2)
        ctk.CTkButton(med_buttons_frame, text="DELETE", command=self.DeleteMed, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", expand=True, padx=2)
        ctk.CTkButton(med_buttons_frame, text="CLEAR", command=self.ClearMed, fg_color="#555555", hover_color="#333333").pack(side="left", expand=True, padx=2)
        med_table_frame = ctk.CTkFrame(add_dept_frame)
        med_table_frame.place(relx=0.05, rely=0.52, relwidth=0.9, relheight=0.45)
        sc_y = ttk.Scrollbar(med_table_frame, orient="vertical")
        self.medicine_table = ttk.Treeview(med_table_frame, columns=("ref", "medname"), yscrollcommand=sc_y.set, show="headings")
        sc_y.config(command=self.medicine_table.yview)
        sc_y.pack(side="right", fill="y")
        self.medicine_table.pack(expand=True, fill="both")
        self.medicine_table.heading("ref", text="Ref")
        self.medicine_table.heading("medname", text="Medicine Name")
        self.medicine_table.column("ref", width=80)
        self.medicine_table.column("medname", stretch=tkinter.YES)
        self.medicine_table.bind("<ButtonRelease-1>", self.Medget_cursor)

        # Button and Search Frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky="ew")
        ctk.CTkButton(button_frame, text="ADD MEDICINE", command=self.add_data).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="UPDATE", command=self.update_data).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="DELETE", command=self.delete_data, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="RESET", command=self.reset_data, fg_color="#555555", hover_color="#333333").pack(side="left", padx=5, pady=10)
        ctk.CTkLabel(button_frame, text="Search By:").pack(side="left", padx=(20, 5), pady=10)
        ctk.CTkComboBox(button_frame, variable=self.search_combo_var, values=["Ref_no", "MedName", "LotNo"], state="readonly").pack(side="left", padx=5, pady=10)
        ctk.CTkEntry(button_frame, textvariable=self.txtSearch_var, placeholder_text="Enter search term...").pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="SEARCH", command=self.search_data).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="SHOW ALL", command=self.fetch_data).pack(side="left", padx=5, pady=10)
        ctk.CTkButton(button_frame, text="EXIT", command=self.root.quit, fg_color="#D32F2F", hover_color="#B71C1C").pack(side="right", padx=5, pady=10)

        # Main Data Table
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(0, 0))
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        cols = ("reg", "companyname", "type", "tabletname", "lotno", "issuedate", "expdate", "uses", "sideeffect", "warning", "dosage", "price", "productqt")
        self.pharmacy_table = ttk.Treeview(table_frame, columns=cols, show="headings", xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        scroll_x.config(command=self.pharmacy_table.xview)
        scroll_y.config(command=self.pharmacy_table.yview)
        headings = [("reg", "Ref No"), ("companyname", "Company"), ("type", "Med Type"), ("tabletname", "Med Name"), ("lotno", "Lot No"), ("issuedate", "Issue Date"), ("expdate", "Exp Date"), ("uses", "Uses"), ("sideeffect", "Side Effect"), ("warning", "Warning"), ("dosage", "Dosage"), ("price", "Price"), ("productqt", "Qty")]
        for col, text in headings:
            self.pharmacy_table.heading(col, text=text, anchor="w")
            self.pharmacy_table.column(col, width=120, minwidth=100, anchor="w")
        self.pharmacy_table.pack(fill="both", expand=True)
        self.pharmacy_table.bind("<ButtonRelease-1>", self.get_cursor_data)
        
    def set_language(self, language):
        self.chat_language = language
        accent_color = self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        if language == 'English':
            self.en_button.configure(fg_color=accent_color)
            self.hi_button.configure(fg_color="gray40")
        else:
            self.hi_button.configure(fg_color=accent_color)
            self.en_button.configure(fg_color="gray40")

    def add_chat_bubble(self, message, is_user):
        if is_user:
            anchor_side, color = "e", self.root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        else:
            anchor_side, color = "w", "gray25"

        bubble_frame = ctk.CTkFrame(self.chat_display_frame, fg_color="transparent")
        bubble_frame.pack(fill="x", padx=5, pady=2)
        
        # Increased wraplength for wider chat bubbles
        label = ctk.CTkLabel(bubble_frame, text=message, fg_color=color, corner_radius=15, 
                             wraplength=600, justify="left", text_color="white")
        label.pack(anchor=anchor_side, padx=5, pady=2, ipady=5, ipadx=8)

        # Auto-scroll to the new message
        self.root.after(100, lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
    
    def send_chat_message(self, event=None):
        user_input = self.chat_message_var.get()
        if not user_input.strip():
            return

        self.add_chat_bubble(user_input, is_user=True)
        self.chat_message_var.set("")
        self.root.update_idletasks()
        
        thinking_bubble_frame = ctk.CTkFrame(self.chat_display_frame, fg_color="transparent")
        thinking_bubble_frame.pack(fill="x", padx=5, pady=2)
        thinking_bubble = ctk.CTkLabel(thinking_bubble_frame, text="...", fg_color="gray25", corner_radius=15)
        thinking_bubble.pack(anchor='w', padx=10, pady=2, ipady=5, ipadx=8)
        self.chat_display_frame._parent_canvas.yview_moveto(1.0)
        self.root.update_idletasks()

        def get_ai_response():
            try:
                # IMPORTANT: Replace with your actual Google Generative AI API key
                api_key = "YOUR_GOOGLE_AI_API_KEY"
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""You are a helpful AI Pharmacy Assistant. A user is asking about a medicine.
                Provide a clear, concise, and easy-to-understand summary for the following medicine: '{user_input}'.
                Your response MUST be in the following language: {self.chat_language}.
                Include these points if possible:
                1.  **Primary Use:**
                2.  **Dosage Info:**
                3.  **Important Advice:**
                At the end, you MUST include this disclaimer in the same language of the response:
                'Disclaimer: This is AI-generated information and not a substitute for professional medical advice. Always consult a doctor or pharmacist.'"""
                response = model.generate_content(prompt)
                ai_text = response.text.strip()
                self.root.after(0, thinking_bubble_frame.destroy)
                self.root.after(0, self.add_chat_bubble, ai_text, False)

            except Exception as e:
                error_message = f"AI: Sorry, an error occurred.\nError: {e}"
                self.root.after(0, thinking_bubble_frame.destroy)
                self.root.after(0, self.add_chat_bubble, error_message, False)
        
        threading.Thread(target=get_ai_response, daemon=True).start()

    def db_connect(self):
        try:
            # IMPORTANT: Replace with your actual database credentials
            conn = mysql.connector.connect(host="localhost", 
                                           username="root", 
                                           password="your_mysql_password", 
                                           database="mydata")
            return conn, conn.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}", parent=self.root)
            return None, None

    def update_medicine_name_list(self):
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            my_cursor.execute("SELECT DISTINCT medname FROM pharmaa ORDER BY medname ASC")
            rows = my_cursor.fetchall()
            med_names = [row[0] for row in rows if row[0]]
            self.comMedName.configure(values=med_names if med_names else [""])
        finally:
            if conn: conn.close()
    
    def AddMed(self):
        if not self.refMed_var.get() or not self.addmed_var.get():
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            my_cursor.execute("INSERT INTO pharmaa(ref, medname) VALUES (%s, %s)", (self.refMed_var.get(), self.addmed_var.get()))
            conn.commit()
            self.fetch_datamed()
            self.ClearMed()
            self.update_medicine_name_list()
            messagebox.showinfo("Success", "Medicine Type Added", parent=self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
        finally:
            if conn: conn.close()

    def UpdateMed(self):
        if not self.refMed_var.get() or not self.addmed_var.get():
            messagebox.showerror("Error", "All Fields are Required", parent=self.root)
            return
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            my_cursor.execute("UPDATE pharmaa SET medname=%s WHERE ref=%s", (self.addmed_var.get(), self.refMed_var.get()))
            conn.commit()
            self.fetch_datamed()
            self.ClearMed()
            self.update_medicine_name_list()
            messagebox.showinfo("Success", "Medicine Type has been updated", parent=self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
        finally:
            if conn: conn.close()

    def DeleteMed(self):
        if not self.refMed_var.get():
            messagebox.showerror("Error", "Reference no must be selected", parent=self.root)
            return
        if messagebox.askyesno("Confirm Delete", f"Do you want to delete {self.addmed_var.get()}?", parent=self.root):
            conn, my_cursor = self.db_connect()
            if not conn: return
            try:
                my_cursor.execute("DELETE from pharmaa where ref=%s", (self.refMed_var.get(),))
                conn.commit()
                self.fetch_datamed()
                self.ClearMed()
                self.update_medicine_name_list()
                messagebox.showinfo("Deleted", "Medicine Type has been Deleted", parent=self.root)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
            finally:
                if conn: conn.close()

    def fetch_datamed(self):
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            my_cursor.execute("SELECT * FROM pharmaa")
            rows = my_cursor.fetchall()
            self.medicine_table.delete(*self.medicine_table.get_children())
            for i in rows:
                self.medicine_table.insert("", "end", values=i)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching medicine types: {err}", parent=self.root)
        finally:
            if conn: conn.close()
    
    def Medget_cursor(self, event=""):
        try:
            cursor_row = self.medicine_table.focus()
            if not cursor_row: return
            content = self.medicine_table.item(cursor_row)
            row = content["values"]
            self.refMed_var.set(str(row[0]))
            self.addmed_var.set(str(row[1]))
        except (IndexError, tkinter.TclError):
            pass
    
    def ClearMed(self):
        self.refMed_var.set("")
        self.addmed_var.set("")
    
    def add_data(self):
        if not self.ref_var.get() or not self.lot_var.get():
            messagebox.showerror("Error", "Reference No and Lot No are required", parent=self.root)
            return
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            sql = "INSERT INTO pharmacy (Ref_no, CmpName, TypeMed, MedName, LotNo, IssueDate, ExpDate, uses, SideEffect, warning, dosage, price, product) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (self.ref_var.get(), self.cmpName_var.get(), self.medType_var.get(), self.medName_var.get(), self.lot_var.get(), self.issueDate_var.get(), self.expDate_var.get(), self.uses_var.get(), self.sideEffect_var.get(), self.warning_var.get(), self.dosage_var.get(), self.price_var.get(), self.product_var.get())
            my_cursor.execute(sql, val)
            conn.commit()
            self.fetch_data()
            self.reset_data()
            messagebox.showinfo("Success", "Data has been added", parent=self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
        finally:
            if conn: conn.close()
    
    def fetch_data(self):
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            my_cursor.execute("SELECT Ref_no, CmpName, TypeMed, MedName, LotNo, IssueDate, Expdate, uses, SideEffect, warning, dosage, price, product FROM pharmacy")
            rows = my_cursor.fetchall()
            self.pharmacy_table.delete(*self.pharmacy_table.get_children())
            for i in rows:
                self.pharmacy_table.insert("", "end", values=i)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not fetch data: {err}", parent=self.root)
        finally:
            if conn: conn.close()

    def get_cursor_data(self, event=""):
        try:
            cursor_row = self.pharmacy_table.focus()
            if not cursor_row: return
            content = self.pharmacy_table.item(cursor_row)
            row = content["values"]
            self.ref_var.set(row[0])
            self.cmpName_var.set(row[1])
            self.medType_var.set(row[2])
            self.medName_var.set(row[3])
            self.lot_var.set(row[4])
            self.issueDate_var.set(row[5])
            self.expDate_var.set(row[6])
            self.uses_var.set(row[7])
            self.sideEffect_var.set(row[8])
            self.warning_var.set(row[9])
            self.dosage_var.set(row[10])
            self.price_var.set(row[11])
            self.product_var.set(row[12])
        except (IndexError, tkinter.TclError):
            pass

    def update_data(self):
        if not self.ref_var.get():
            messagebox.showerror("Error", "Select a record to update", parent=self.root)
            return
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            sql = "UPDATE pharmacy SET CmpName=%s, TypeMed=%s, MedName=%s, LotNo=%s, IssueDate=%s, ExpDate=%s, uses=%s, SideEffect=%s, warning=%s, dosage=%s, price=%s, product=%s WHERE Ref_no=%s"
            val = (self.cmpName_var.get(), self.medType_var.get(), self.medName_var.get(), self.lot_var.get(), self.issueDate_var.get(), self.expDate_var.get(), self.uses_var.get(), self.sideEffect_var.get(), self.warning_var.get(), self.dosage_var.get(), self.price_var.get(), self.product_var.get(), self.ref_var.get())
            my_cursor.execute(sql, val)
            conn.commit()
            self.fetch_data()
            self.reset_data()
            messagebox.showinfo("Success", "Record has been updated", parent=self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
        finally:
            if conn: conn.close()

    def delete_data(self):
        if not self.ref_var.get():
            messagebox.showerror("Error", "Select a record to delete", parent=self.root)
            return
        if messagebox.askyesno("Confirm Delete", f"Do you want to delete record with Ref No: {self.ref_var.get()}?", parent=self.root):
            conn, my_cursor = self.db_connect()
            if not conn: return
            try:
                my_cursor.execute("DELETE FROM pharmacy WHERE Ref_no=%s", (self.ref_var.get(),))
                conn.commit()
                self.fetch_data()
                self.reset_data()
                messagebox.showinfo("Deleted", "Record has been deleted", parent=self.root)
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error: {err}", parent=self.root)
            finally:
                if conn: conn.close()

    def reset_data(self):
        for var in [self.ref_var, self.cmpName_var, self.medType_var, self.medName_var, 
                    self.lot_var, self.issueDate_var, self.expDate_var, self.uses_var, 
                    self.sideEffect_var, self.warning_var, self.dosage_var, 
                    self.price_var, self.product_var, self.txtSearch_var]:
            var.set("")
        self.fetch_data()

    def search_data(self):
        if not self.txtSearch_var.get():
            messagebox.showerror("Error", "Please enter a search term", parent=self.root)
            return
        conn, my_cursor = self.db_connect()
        if not conn: return
        try:
            search_column = self.search_combo_var.get()
            # Use backticks for column names to avoid SQL errors with special characters or keywords
            sql = f"SELECT * FROM pharmacy WHERE `{search_column}` LIKE %s"
            val = ('%' + self.txtSearch_var.get() + '%',)
            my_cursor.execute(sql, val)
            rows = my_cursor.fetchall()
            self.pharmacy_table.delete(*self.pharmacy_table.get_children())
            if rows:
                for i in rows:
                    self.pharmacy_table.insert("", "end", values=i)
            else:
                messagebox.showinfo("Not Found", "No records match your search", parent=self.root)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during search: {err}", parent=self.root)
        finally:
            if conn: conn.close()

if __name__ == "__main__":
    root = ctk.CTk()
    app = PharmacyManagementSystem(root)
    root.mainloop()