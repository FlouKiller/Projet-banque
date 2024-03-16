from tkinter import *
from tkinter import messagebox
import sqlite3
from random import randint

root = Tk()
root.resizable(width=False, height=False)

bdd = sqlite3.connect("banque.db")
curseur = bdd.cursor()

def generate_id(lenght):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    result = ""
    for i in range(lenght):
        result += chars[randint(0, len(chars)-1)]
    return result

def menu_principal():
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Banque - Menu principal")
    root.geometry("540x360")

    button_connexion = Button(text="Connexion à un compte", font=("Helvetica", 20), command=identification)
    button_enregistrement = Button(text="Créer un compte", font=("Helvetica", 20))

    button_connexion.place(x=115, y=110)
    button_enregistrement.place(x=150, y=190)


def identification():

    def connexion():
        if id_textbox.get() == "" or password_textbox.get() == "":
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return

        requete = "SELECT * FROM infos_clients WHERE identifiant = ?"
        curseur.execute(requete, [id_textbox.get()])
        resultat = curseur.fetchall()
        if resultat == []:
            messagebox.showerror("Erreur", "Identifiant inconnu")
            return
        client = resultat[0]
        if client[4] != password_textbox.get():
            messagebox.showerror("Erreur", "Mot de passe incorrect")
            return
        
        interface_utilisateur(client)


    for widget in root.winfo_children():
        widget.destroy()

    root.title("Banque - Connexion")
    root.geometry("540x360")

    id_label = Label(text="Identifiant :", font=("Helvetica", 15))
    password_label = Label(text="Mot de passe :", font=("Helvetica", 15))
    id_textbox = Entry(width=20, font=("Helvetica", 15), justify="center")
    password_textbox = Entry(width=20, show="•", font=("Helvetica", 15), justify="center")
    connexion_button = Button(text="Se connecter", font=("Helvetica", 15), command=connexion)

    button_retour = Button(text="Retour", font=("Helvetica", 15), command=menu_principal)

    id_label.place(x=220, y=50)
    password_label.place(x=205, y=120)
    id_textbox.place(x=155, y=80)
    password_textbox.place(x=155, y=150)
    connexion_button.place(x=200, y=200)

    button_retour.place(x=450, y=310)


def interface_utilisateur(client):
        
    requete = "SELECT * FROM comptes WHERE identifiant_proprietaire = ?"
    curseur.execute(requete, [client[0]])
    comptes = curseur.fetchall()
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.title("Banque - Espace Client")
    root.geometry("1080x720")
    
    name_label = Label(text="Bienvenue, M. ou Mme. " + client[1] + " " + client[2], font=("Helvetica", 15))
    account_management_button = Button(text="Gestion des comptes", font=("Helvetica", 15), command=lambda:account_management(client))
    
    disconnct_button = Button(text="Se déconnecter", font=("Helvetica", 12), command=identification)
    
    name_label.place(x=10, y=10)
    disconnct_button.place(x=945, y=680)
    account_management_button.place(x=870, y=5)


def account_management(client):

    def open_or_close_account(account, button):
        if "Ouvrir" in button["text"]:
            question = messagebox.askquestion("Confirmation", "Voulez vous vraiment ouvrir un Livret " + ("A ?" if account == 1 else "B ?"))
            if question == "no":
                return account_management(client)
            
            id_account = generate_id(15)
            requete = "SELECT * FROM comptes WHERE numero_compte = ?"
            curseur.execute(requete, [id_account])
            while curseur.fetchall() != []:
                id_account = generate_id(15)
                requete = "SELECT * FROM comptes WHERE numero_compte = ?"
                curseur.execute(requete, [id_account])
            
            requete = "INSERT INTO comptes (numero_compte, identifiant_proprietaire, type_compte, montant) VALUES (?, ?, ?, ?)"
            curseur.execute(requete, [id_account, client[0], account, 0])
            bdd.commit()
        else:
            question = messagebox.askquestion("Confirmation", "Voulez vous clôturer votre Livret " + ("A ?" if account == 1 else "B ?"))
            if question == "no":
                return account_management(client)
            
            requete = "SELECT montant FROM comptes WHERE identifiant_proprietaire = ? AND type_compte = ?"
            curseur.execute(requete, [client[0], account])
            montant = curseur.fetchall()[0][0]
            if montant != 0:
                messagebox.showerror("Erreur", "Vous ne pouvez pas supprimer un compte sur lequel il reste des fonds.")
                return account_management(client)
            
            requete = "DELETE FROM comptes WHERE identifiant_proprietaire = ? AND type_compte = ?"
            curseur.execute(requete, [client[0], account])
            bdd.commit()
            
        account_management(client)
        
    
    for widget in root.winfo_children():
        widget.destroy()
    
    root.title("Banque - Gestion des comptes")
    root.geometry("540x360")
    
    livret_a_state = False
    livret_b_state = False
    
    livret_a_button = Button(text="Ouvrir un Livret A", font=("Helvetica", 15), command=lambda:open_or_close_account(1, livret_a_button))
    livret_b_button = Button(text="Ouvrir un Livret B", font=("Helvetica", 15), command=lambda:open_or_close_account(2, livret_b_button))
    
    requete = "SELECT * FROM comptes WHERE identifiant_proprietaire = ? AND type_compte = 1"
    curseur.execute(requete, [client[0]])
    if curseur.fetchall() != []:
        livret_a_state = True
        livret_a_button["text"] = "Clôturer le Livret A"
        
    requete = "SELECT * FROM comptes WHERE identifiant_proprietaire = ? AND type_compte = 2"
    curseur.execute(requete, [client[0]])
    if curseur.fetchall() != []:
        livret_b_state = True
        livret_b_button["text"] = "Clôturer le Livret B"
    
    livret_a_button.place(x=180, y=120)
    livret_b_button.place(x=180, y=170)
    
    back_button = Button(text="Retour", font=("Helvetica", 12), command=lambda:interface_utilisateur(client))
    back_button.place(x=475, y=325)
    

menu_principal()
root.mainloop()