import tkinter as tk
from tkinter import ttk
import sqlite3

class Passwords:

    db_filename = "passwords.db"

    def __init__(self, root):
        self.root = root
        self.create_gui()
        ttk.style = ttk.Style()
        ttk.style.configure("Treeview", font=("helvetica", 10))
        ttk.style.configure("Treeview.Heading", font=("helvetica", 12, "bold"))

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result

    def create_gui(self):
        self.create_left_icon()
        self.create_label_frame()
        self.create_message_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_passwords()

    def create_left_icon(self):
        photo = tk.PhotoImage(file='icons/logo.gif')
        label = tk.Label(image=photo)
        label.image = photo
        label.grid(row=0, column=0)

    def create_label_frame(self):
        labelframe = tk.LabelFrame(self.root, text='Agregar nueva contraseña', bg="deepskyblue3", font="helvetica 10")
        labelframe.grid(row=0, column=1, padx=8, sticky="ew")
        tk.Label(labelframe, text='Usuario: ', bg="deepskyblue3", fg="black").grid(row=1, column=1, sticky="W", pady=2,
                                                                                   padx=15)
        self.namefield = tk.Entry(labelframe)
        self.namefield.grid(row=1, column=2, sticky="W", padx=5, pady=2)
        tk.Label(labelframe, text='Aplicación: ', bg="deepskyblue3", fg="black").grid(row=2, column=1, sticky="w", pady=2,
                                                                                       padx=15)
        self.emailfield = tk.Entry(labelframe)
        self.emailfield.grid(row=2, column=2, sticky="W", padx=5, pady=2)
        tk.Label(labelframe, text='Contraseña: ', bg="deepskyblue3", fg="black").grid(row=3, column=1, sticky="w", pady=2,
                                                                                      padx=15)
        self.numfield = tk.Entry(labelframe)  
        self.numfield.grid(row=3, column=2, sticky="W", padx=5, pady=2)
        tk.Button(labelframe, text='Agregar contraseña', command=self.on_add_password_button_clicked, bg="blue4",
                  fg="white").grid(row=4, column=2, sticky="E", padx=5, pady=5)

    def create_message_area(self):
        self.message = tk.Label(text="", fg="red")
        self.message.grid(row=3, column=1, sticky="W")

    def create_tree_view(self):
        self.tree = ttk.Treeview(height=10, columns=("page", "pass"), style="Treeview")
        self.tree.grid(row=6, column=0, columnspan=3)
        self.tree.heading("#0", text="Nombre", anchor="w")
        self.tree.heading("page", text="Aplicación", anchor="w")
        self.tree.heading("pass", text="Contraseña", anchor="w")


    def create_scrollbar(self):
        self.scrollbar = tk.Scrollbar(orient="vertical", command=self.tree.yview)
        self.scrollbar.grid(row=6, column=3, rowspan=10, sticky="sn")
        self.tree.config(yscrollcommand=self.scrollbar.set)

    def create_bottom_buttons(self):
        tk.Button(text="Eliminar contraseña", command=self.on_delete_selected_button_clicked, bg="firebrick3",
                  fg="white").grid(row=8, column=2, sticky="w", pady=10, padx=20)
        tk.Button(text="Modificar contraseña", command=self.on_modify_selected_button_clicked, bg="blue4",
                  fg="white").grid(row=8, column=1, sticky="E")
        tk.Button(text="Mostrar contraseña", command=self.show_password_popup, bg="green", fg="white").grid(row=8,column=0, sticky="W", pady=10,padx=20)

    def on_add_password_button_clicked(self):
        self.add_new_password()


    def on_delete_selected_button_clicked(self):
        self.message["text"] = ''
        try:
            self.tree.item(self.tree.selection())["values"][0]
        except IndexError as e:
            self.message["text"] = 'No se ha seleccionado contraseña a eliminar'
            return
        self.delete_passwords()

    def on_modify_selected_button_clicked(self):
        self.message["text"] = ""
        try:
            self.tree.item(self.tree.selection())["values"][0]
        except IndexError as e:
            self.message["text"] = "No se ha seleccionado contraseña a modificar"
            return
        self.open_modify_window()

    def show_password_popup(self):
        selected_item = self.tree.selection()
        if selected_item:
            user_name = self.tree.item(selected_item)["text"]
            query = "SELECT page, pass FROM password_list WHERE user_name = ?"
            result = self.execute_db_query(query, (user_name,))
            row = result.fetchone()
            if row:
                page, password = row
                popup = tk.Toplevel()
                popup.title("Mostrar Contraseña")
                tk.Label(popup, text="Usuario: {}".format(user_name)).grid(row=0, column=0, sticky="W", padx=10, pady=5)
                tk.Label(popup, text="Aplicación: {}".format(page)).grid(row=1, column=0, sticky="W", padx=10, pady=5)
                tk.Label(popup, text="Contraseña: {}".format(password)).grid(row=2, column=0, sticky="W", padx=10, pady=5)
            else:
                self.message["text"] = 'No se encontró información para el usuario seleccionado'
        else:
            self.message["text"] = 'No se ha seleccionado contraseña para mostrar'



    def add_new_password(self):
        if self.new_password_validated():
            query = 'INSERT INTO password_list VALUES(NULL,?, ?,?)'
            parameters = (self.namefield.get(), self.emailfield.get(), self.numfield.get())
            self.execute_db_query(query, parameters)
            self.message['text'] = 'Contraseña de {} agregada.'.format(self.emailfield.get())
            self.numfield.delete(0, tk.END)   
            self.namefield.delete(0, tk.END)
            self.emailfield.delete(0, tk.END)
            self.view_passwords()
        else:
            self.message['text'] = 'Debes completar todos los datos.'
            self.view_passwords()

    def new_password_validated(self):
        return len(self.namefield.get()) != 0 and len(self.emailfield.get()) != 0 and len(self.numfield.get()) != 0

    def view_passwords(self):
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)
        query = "SELECT * FROM password_list ORDER BY user_name DESC"
        password_entries = self.execute_db_query(query)
        for row in password_entries:
            self.tree.insert("", 0, text=row[1], values=(row[2], '*' * len(row[3])))


    def delete_passwords(self):
        self.message["text"] = ''
        user_name = self.tree.item(self.tree.selection())["text"]
        page = self.tree.item(self.tree.selection())["values"][0]
        query = "DELETE FROM password_list WHERE user_name= ?"
        self.execute_db_query(query, (user_name,))
        self.message["text"] = "Usuario {} de {} eliminado".format(user_name, page)
        self.view_passwords()


    def open_modify_window(self):
        user_name = self.tree.item(self.tree.selection())["text"]
        old_pass = self.tree.item(self.tree.selection())["values"][1]
        self.transient = tk.Toplevel()
        self.transient.title("Actualizar contraseña")
        tk.Label(self.transient, text="Usuario: ").grid(row=0, column=1)
        tk.Entry(self.transient, textvariable=tk.StringVar(
            self.transient, value=user_name), state="readonly").grid(row=0, column=2)

        tk.Label(self.transient, text='Contraseña actual:').grid(row=1, column=1)
        tk.Entry(self.transient, textvariable=tk.StringVar(
            self.transient, value=old_pass), state='readonly').grid(row=1, column=2)
        tk.Label(self.transient, text='Nueva contraseña:').grid(
            row=2, column=1)
        new_pass_entry_widget = tk.Entry(self.transient, show='*')  
        new_pass_entry_widget.grid(row=2, column=2)

        tk.Button(self.transient, text="Actualizar contraseña", command=lambda: self.update_passwords(
            new_pass_entry_widget.get(), old_pass, user_name), bg="blue4", fg="white").grid(row=3, column=2, sticky="E")

        self.transient.mainloop()

    def update_passwords(self, newpass, old_pass, user_name):
        if not newpass:
            self.message["text"] = "Debes ingresar una nueva contraseña."
            return

        query = "UPDATE password_list SET pass=? WHERE pass=? AND user_name=?"
        parameters = (newpass, old_pass, user_name)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message["text"] = "Contraseña del usuario {} modificada".format(user_name)
        self.view_passwords()


        


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Gestor de contraseñas')
    root.geometry("620x420")
    root.resizable(width=False, height=False)
    application = Passwords(root)
    root.mainloop()
