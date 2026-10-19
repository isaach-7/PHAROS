# main.py
import customtkinter as ctk
import re
from dbManager import initialiseDatabase, getUserByUsername
from authManager import loginUser, registerUser
from PIL import Image

# ──────────────────────────────────────────────
#  App-wide colour constants
# ──────────────────────────────────────────────
BLUE_PRIMARY   = "#1A73E8"
BLUE_DARK      = "#1558B0"
RED_LOGOUT     = "#E53935"
RED_LOGOUT_HOV = "#C62828"
GREEN_PRIMARY  = "#2E7D32"
GREEN_HOVER    = "#1B5E20"
CARD_LIGHT     = "#FFFFFF"
CARD_DARK      = "#2B2B2B"

# ──────────────────────────────────────────────
#  Session state
# ──────────────────────────────────────────────
currentUser   = ""
currentUserId = None

# ══════════════════════════════════════════════
#  Main application class
# ══════════════════════════════════════════════
class PharosApp(ctk.CTk):

    def __init__(self):
        self.currentUserId = None
        self.currentUser   = ""
        super().__init__()
        self.title("PHAROS")
        self.geometry("1200x700")
        self.resizable(False, False)

        self.darkMode = False
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        initialiseDatabase()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for FrameClass in (LoginFrame, HomeFrame,
                           DiagnosisFrame, CatalogueFrame, PrescriptionFrame):
            frame = FrameClass(parent=self.container, controller=self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame("LoginFrame")

    def showFrame(self, frameName):
        frame = self.frames[frameName]
        frame.tkraise()

    def toggleDarkMode(self):
        self.darkMode = not self.darkMode
        mode = "dark" if self.darkMode else "light"
        ctk.set_appearance_mode(mode)
        for frame in self.frames.values():
            if hasattr(frame, "refreshTheme"):
                frame.refreshTheme()

    def openDiagnosisPage(self):
        self.frames["DiagnosisFrame"].showDisclaimer()
        self.showFrame("DiagnosisFrame")

    def openCataloguePage(self):
        self.frames["CatalogueFrame"].loadProducts()
        self.showFrame("CatalogueFrame")

    def openPrescriptionPage(self):
        self.frames["PrescriptionFrame"].loadPrescriptions()
        self.showFrame("PrescriptionFrame")

    def logoutUser(self):
        global currentUser, currentUserId
        self.currentUserId = None
        self.currentUser   = ""
        currentUser   = ""
        currentUserId = None
        loginFrame = self.frames["LoginFrame"]
        loginFrame.usernameEntry.delete(0, "end")
        loginFrame.passwordEntry.delete(0, "end")
        self.showFrame("LoginFrame")


# ══════════════════════════════════════════════
#  Shared title bar
# ══════════════════════════════════════════════
def buildTitleBar(parent, controller):
    titleBar = ctk.CTkFrame(parent, height=80, corner_radius=0,
                             fg_color=(BLUE_PRIMARY, "#16213E"))
    titleBar.pack(fill="x", side="top")
    titleBar.pack_propagate(False)

    titleGroup = ctk.CTkFrame(titleBar, fg_color="transparent")
    titleGroup.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(titleGroup, text="PHAROS",
                 font=ctk.CTkFont("Segoe UI", 34, "bold"),
                 text_color="white").pack()
    ctk.CTkLabel(titleGroup,
                 text="Pharmaceutical Health Advice & Recommendations Online System",
                 font=ctk.CTkFont("Segoe UI", 11),
                 text_color="white").pack()

    toggleBtn = ctk.CTkButton(
        titleBar, text="🌙  Dark Mode", width=130, height=34,
        fg_color="#3A3ACA", hover_color="#2B2BAA",
        text_color="white",
        font=ctk.CTkFont(size=12, weight="bold"),
        corner_radius=20,
        command=controller.toggleDarkMode)
    toggleBtn.place(relx=0.97, rely=0.5, anchor="e")

    return titleBar, toggleBtn


# ══════════════════════════════════════════════
#  Login Frame
# ══════════════════════════════════════════════
class LoginFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._buildUI()

    def _buildUI(self):
        titleBar, self.toggleBtn = buildTitleBar(self, self.controller)

        contentRow = ctk.CTkFrame(self, fg_color="transparent")
        contentRow.pack(expand=True, fill="both", padx=80, pady=20)
        contentRow.grid_columnconfigure((0, 1), weight=1, uniform="half")
        contentRow.grid_rowconfigure(0, weight=1)

        loginPanel = ctk.CTkFrame(contentRow, corner_radius=16,
                                   fg_color=(CARD_LIGHT, CARD_DARK),
                                   border_width=1,
                                   border_color=("#D0D8E8", "#3A3A5C"))
        loginPanel.grid(row=0, column=0, padx=(0, 16), pady=10, sticky="nsew")
        self._buildLoginPanel(loginPanel)

        registerPanel = ctk.CTkFrame(contentRow, corner_radius=16,
                                      fg_color=(CARD_LIGHT, CARD_DARK),
                                      border_width=1,
                                      border_color=("#D0D8E8", "#3A3A5C"))
        registerPanel.grid(row=0, column=1, padx=(16, 0), pady=10, sticky="nsew")
        self._buildRegisterPanel(registerPanel)

        ctk.CTkLabel(
            self,
            text="Your data is securely stored and kept private. Not associated with NHS systems.",
            font=ctk.CTkFont(size=11),
            text_color="gray").pack(side="bottom", pady=(0, 10))

    def _buildLoginPanel(self, parent):
        ctk.CTkLabel(parent, text="Login",
                     font=ctk.CTkFont("Segoe UI", 22, "bold")).pack(pady=(28, 16))

        ctk.CTkLabel(parent, text="Username",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=36)
        self.usernameEntry = ctk.CTkEntry(parent, width=280, height=40,
                                           placeholder_text="Enter username")
        self.usernameEntry.pack(padx=36, pady=(4, 12))

        ctk.CTkLabel(parent, text="Password",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=36)
        self.passwordEntry = ctk.CTkEntry(parent, width=280, height=40,
                                           placeholder_text="Enter password",
                                           show="*")
        self.passwordEntry.pack(padx=36, pady=(4, 6))

        self.showPasswordVar = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(parent, text="Show password",
                         variable=self.showPasswordVar,
                         font=ctk.CTkFont(size=12),
                         command=self._toggleShowPassword).pack(
                             padx=36, pady=(0, 14), anchor="w")

        self.loginErrorLabel = ctk.CTkLabel(parent, text="",
                                             font=ctk.CTkFont(size=12),
                                             text_color="#E53935")
        self.loginErrorLabel.pack()

        ctk.CTkButton(parent, text="Log In", width=280, height=42,
                      fg_color=BLUE_PRIMARY, hover_color=BLUE_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.attemptLogin).pack(pady=(4, 28), padx=36)

    def _buildRegisterPanel(self, parent):
        ctk.CTkLabel(parent, text="Register",
                     font=ctk.CTkFont("Segoe UI", 22, "bold")).pack(pady=(28, 16))

        ctk.CTkLabel(parent, text="Username",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=36)
        self.newUsernameEntry = ctk.CTkEntry(parent, width=280, height=40,
                                              placeholder_text="Choose a username")
        self.newUsernameEntry.pack(padx=36, pady=(4, 12))

        ctk.CTkLabel(parent, text="Password",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=36)
        self.newPasswordEntry = ctk.CTkEntry(parent, width=280, height=40,
                                              placeholder_text="Choose a password",
                                              show="*")
        self.newPasswordEntry.pack(padx=36, pady=(4, 12))

        ctk.CTkLabel(parent, text="Confirm Password",
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=36)
        self.confirmPasswordEntry = ctk.CTkEntry(parent, width=280, height=40,
                                                  placeholder_text="Repeat password",
                                                  show="*")
        self.confirmPasswordEntry.pack(padx=36, pady=(4, 14))

        self.registerErrorLabel = ctk.CTkLabel(parent, text="",
                                                font=ctk.CTkFont(size=12),
                                                text_color="#E53935",
                                                wraplength=260)
        self.registerErrorLabel.pack()

        ctk.CTkButton(parent, text="Create Account", width=280, height=42,
                      fg_color=GREEN_PRIMARY, hover_color=GREEN_HOVER,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.attemptRegister).pack(pady=(4, 28), padx=36)

    def _toggleShowPassword(self):
        show = "" if self.showPasswordVar.get() else "*"
        self.passwordEntry.configure(show=show)

    def attemptLogin(self):
        global currentUser, currentUserId

        username = self.usernameEntry.get().strip()
        password = self.passwordEntry.get()

        loginSuccess = loginUser(username, password)

        if loginSuccess == "Login successful":
            currentUser = username
            currentUserId = None
            self.controller.currentUser   = username
            self.controller.currentUserId = None

            userRecord = getUserByUsername(username)
            if userRecord:
                currentUserId = userRecord[0]
                self.controller.currentUserId = userRecord[0]

            self.loginErrorLabel.configure(text="")
            self.controller.frames["HomeFrame"].updateWelcome()
            self.controller.showFrame("HomeFrame")
        else:
            self.loginErrorLabel.configure(text=loginSuccess)

    def attemptRegister(self):
        newUsername     = self.newUsernameEntry.get().strip()
        newPassword     = self.newPasswordEntry.get()
        confirmPassword = self.confirmPasswordEntry.get()

        if len(newUsername) < 6:
            self.registerErrorLabel.configure(
                text_color="#E53935",
                text="Username must be at least 6 characters.")
            return

        usernameHasSpace = " " in newUsername
        if usernameHasSpace:
            self.registerErrorLabel.configure(
                text_color="#E53935",
                text="Username cannot contain spaces.")
            return

        usernameHasSpecialChar = bool(re.search(r"[^a-zA-Z0-9]", newUsername))
        if usernameHasSpecialChar:
            self.registerErrorLabel.configure(
                text_color="#E53935",
                text="Username must contain only letters and numbers.")
            return

        passUpper   = bool(re.search(r"[A-Z]",        newPassword))
        passLower   = bool(re.search(r"[a-z]",        newPassword))
        passDigit   = bool(re.search(r"\d",           newPassword))
        passSpecial = bool(re.search(r"[^a-zA-Z0-9]", newPassword))

        if not (passUpper and passLower and passDigit and passSpecial):
            self.registerErrorLabel.configure(
                text_color="#E53935",
                text="Password must contain uppercase, lowercase, a number, and a special character.")
            return

        result = registerUser(newUsername, newPassword, confirmPassword)

        if result == "Registration successful":
            self.registerErrorLabel.configure(
                text_color="#2E7D32",
                text="Account created! Please log in.")
            self.newUsernameEntry.delete(0, "end")
            self.newPasswordEntry.delete(0, "end")
            self.confirmPasswordEntry.delete(0, "end")
        else:
            self.registerErrorLabel.configure(
                text_color="#E53935",
                text=result)

    def refreshTheme(self):
        label  = "🌙  Dark Mode" if not self.controller.darkMode else "☀  Light Mode"
        colour = "#3A3ACA" if self.controller.darkMode else "#E8B000"
        self.toggleBtn.configure(text=label, fg_color=colour)


# ══════════════════════════════════════════════
#  Home Frame
# ══════════════════════════════════════════════
class HomeFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._buildUI()

    def _buildUI(self):
        titleBar, self.toggleBtn = buildTitleBar(self, self.controller)

        self.welcomeLabel = ctk.CTkLabel(
            self, text=f"Welcome, {currentUser}!",
            font=ctk.CTkFont("Segoe UI", 28, "bold"))
        self.welcomeLabel.pack(pady=(28, 8))

        cardsRow = ctk.CTkFrame(self, fg_color="transparent")
        cardsRow.pack(expand=True, fill="both", padx=40, pady=8)
        cardsRow.grid_columnconfigure((0, 1, 2), weight=1, uniform="card")
        cardsRow.grid_rowconfigure(0, weight=1)

        cardData = [
            {
                "title":       "Diagnosis\nTool",
                "description": "Check your symptoms safely with our\nfree online health tool.",
                "icon":        "🩺",
                "command":     self.controller.openDiagnosisPage,
            },
            {
                "title":       "Product\nCatalogue",
                "description": "Browse pharmacy products and view\nproduct information at a glance.",
                "icon":        "💊",
                "command":     self.controller.openCataloguePage,
            },
            {
                "title":       "Prescription\nTracker",
                "description": "View, record and monitor your\nprescriptions with our handy tracker.",
                "icon":        "📋",
                "command":     self.controller.openPrescriptionPage,
            },
        ]

        for col, data in enumerate(cardData):
            card = self._makeCard(cardsRow, **data)
            card.grid(row=0, column=col, padx=18, pady=10, sticky="nsew")

        ctk.CTkLabel(
            self,
            text="Your data is securely stored and kept private. Not associated with NHS systems.",
            font=ctk.CTkFont(size=11),
            text_color="gray").pack(side="bottom", pady=(0, 10))

        ctk.CTkButton(
            self, text="Log out", width=120, height=40,
            fg_color=RED_LOGOUT, hover_color=RED_LOGOUT_HOV,
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=20,
            command=self.controller.logoutUser).pack(side="bottom",
                                                      anchor="e",
                                                      padx=40,
                                                      pady=(0, 6))

    def _makeCard(self, parent, title, description, icon, command):
        card = ctk.CTkFrame(parent, corner_radius=20,
                             fg_color=("#E8E8E8", "#2B2B2B"))

        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     justify="center").pack(pady=(28, 4))

        ctk.CTkLabel(card, text=description,
                     font=ctk.CTkFont(size=12),
                     text_color="gray",
                     justify="center",
                     wraplength=220).pack(padx=16, pady=(0, 16))

        ctk.CTkLabel(card, text=icon,
                     font=ctk.CTkFont(size=72)).pack(pady=(0, 28))

        card.bind("<Enter>", lambda e: card.configure(fg_color=("#D8D8D8", "#333333")))
        card.bind("<Leave>", lambda e: card.configure(fg_color=("#E8E8E8", "#2B2B2B")))

        if command:
            card.bind("<Button-1>", lambda e: command())
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e: command())

        return card

    def updateWelcome(self):
        self.welcomeLabel.configure(text=f"Welcome, {currentUser}!")

    def refreshTheme(self):
        label  = "🌙  Dark Mode" if not self.controller.darkMode else "☀  Light Mode"
        colour = "#3A3ACA" if self.controller.darkMode else "#E8B000"
        self.toggleBtn.configure(text=label, fg_color=colour)


# ══════════════════════════════════════════════
#  Diagnosis Frame
# ══════════════════════════════════════════════
class DiagnosisFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        self.bgQuestions = [
            ("Have you had these symptoms for more than 10 days?",       "yes"),
            ("Are you pregnant?",                                         "yes"),
            ("Are you currently unable to take any medication?",          "yes"),
            ("Do you have any known allergies to common medicines?",      "yes"),
            ("Do you have any long-term medical conditions?",             "yes"),
        ]

        self.diagnosisTrees = {
            "Pain & Discomfort": {
                "question": "Is the pain localised to one specific area?",
                "yes": {
                    "question": "Is the pain sharp or stabbing?",
                    "yes": {
                        "question": "Did the pain start suddenly?",
                        "yes": {
                            "question": "Is the area swollen or bruised?",
                            "yes": {"conclusion": "Possible muscle or joint injury.",
                                    "product": "Ibuprofen Gel"},
                            "no":  {"conclusion": "Possible nerve pain.",
                                    "product": "Paracetamol"}
                        },
                        "no": {
                            "question": "Has the pain lasted more than a week?",
                            "yes": {"conclusion": "Possible chronic pain condition.",
                                    "product": "Co-codamol"},
                            "no":  {"conclusion": "Possible minor injury or strain.",
                                    "product": "Ibuprofen Tablets"}
                        }
                    },
                    "no": {
                        "question": "Is the pain worse when moving?",
                        "yes": {
                            "question": "Is there any swelling in the area?",
                            "yes": {"conclusion": "Possible inflammation or sprain.",
                                    "product": "Ibuprofen Gel"},
                            "no":  {"conclusion": "Possible muscle soreness.",
                                    "product": "Deep Heat Spray"}
                        },
                        "no": {
                            "question": "Do you have a temperature alongside the pain?",
                            "yes": {"conclusion": "Possible infection-related pain.",
                                    "product": "Paracetamol"},
                            "no":  {"conclusion": "Possible tension or postural pain.",
                                    "product": "Ibuprofen Tablets"}
                        }
                    }
                },
                "no": {
                    "question": "Is the pain a general ache across your body?",
                    "yes": {
                        "question": "Do you also have a fever?",
                        "yes": {
                            "question": "Have you recently been in contact with someone who was ill?",
                            "yes": {"conclusion": "Possible viral infection.",
                                    "product": "Paracetamol"},
                            "no":  {"conclusion": "Possible flu-like illness.",
                                    "product": "Lemsip Max"}
                        },
                        "no": {
                            "question": "Are you feeling unusually fatigued?",
                            "yes": {"conclusion": "Possible fatigue-related pain.",
                                    "product": "Vitamin B Complex"},
                            "no":  {"conclusion": "Possible mild body aches.",
                                    "product": "Ibuprofen Tablets"}
                        }
                    },
                    "no": {
                        "question": "Is the pain in your head or neck?",
                        "yes": {
                            "question": "Is the pain throbbing?",
                            "yes": {"conclusion": "Possible migraine or tension headache.",
                                    "product": "Sumatriptan"},
                            "no":  {"conclusion": "Possible tension headache.",
                                    "product": "Paracetamol"}
                        },
                        "no": {
                            "question": "Is the pain in your chest?",
                            "yes": {"conclusion": "Chest pain can be serious. Please seek medical advice.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible general discomfort.",
                                    "product": "Paracetamol"}
                        }
                    }
                }
            },
            "Temperature & Infection Signs": {
                "question": "Do you currently have a temperature above 38°C?",
                "yes": {
                    "question": "Have you had the fever for more than 3 days?",
                    "yes": {
                        "question": "Do you have a rash alongside the fever?",
                        "yes": {
                            "question": "Is the rash spreading rapidly?",
                            "yes": {"conclusion": "Possible serious infection. Seek medical attention.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible viral rash.",
                                    "product": "Antihistamine Tablets"}
                        },
                        "no": {
                            "question": "Do you have difficulty breathing?",
                            "yes": {"conclusion": "Possible respiratory infection. Seek medical advice.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible persistent infection.",
                                    "product": "Paracetamol"}
                        }
                    },
                    "no": {
                        "question": "Do you have a sore throat alongside the fever?",
                        "yes": {
                            "question": "Are your glands swollen?",
                            "yes": {"conclusion": "Possible tonsillitis or throat infection.",
                                    "product": "Throat Lozenges"},
                            "no":  {"conclusion": "Possible viral sore throat.",
                                    "product": "Difflam Spray"}
                        },
                        "no": {
                            "question": "Do you have body aches?",
                            "yes": {"conclusion": "Possible flu.",
                                    "product": "Lemsip Max"},
                            "no":  {"conclusion": "Possible mild fever.",
                                    "product": "Paracetamol"}
                        }
                    }
                },
                "no": {
                    "question": "Do you have chills or feel cold despite a normal temperature?",
                    "yes": {
                        "question": "Do you also have fatigue?",
                        "yes": {
                            "question": "Have symptoms come on suddenly?",
                            "yes": {"conclusion": "Possible early viral infection.",
                                    "product": "Lemsip Max"},
                            "no":  {"conclusion": "Possible ongoing immune response.",
                                    "product": "Vitamin C Tablets"}
                        },
                        "no": {
                            "question": "Do you feel shivery after being outdoors?",
                            "yes": {"conclusion": "Possible exposure-related response.",
                                    "product": "Paracetamol"},
                            "no":  {"conclusion": "Possible mild immune response.",
                                    "product": "Vitamin C Tablets"}
                        }
                    },
                    "no": {
                        "question": "Do you have swollen glands?",
                        "yes": {
                            "question": "Do you also have a sore throat?",
                            "yes": {"conclusion": "Possible throat infection.",
                                    "product": "Throat Lozenges"},
                            "no":  {"conclusion": "Possible lymph node reaction.",
                                    "product": "Ibuprofen Tablets"}
                        },
                        "no": {
                            "question": "Do you feel generally unwell without a clear cause?",
                            "yes": {"conclusion": "Possible early infection.",
                                    "product": "Vitamin C Tablets"},
                            "no":  {"conclusion": "No clear infection signs at this time.",
                                    "product": "Paracetamol"}
                        }
                    }
                }
            },
            "Respiratory Symptoms": {
                "question": "Do you have a cough?",
                "yes": {
                    "question": "Is the cough producing mucus?",
                    "yes": {
                        "question": "Is the mucus green or yellow?",
                        "yes": {
                            "question": "Do you also have a fever?",
                            "yes": {"conclusion": "Possible chest infection.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible productive cough.",
                                    "product": "Benylin Chesty Cough"}
                        },
                        "no": {
                            "question": "Have you had the cough for more than 2 weeks?",
                            "yes": {"conclusion": "Persistent cough — see a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible chesty cough.",
                                    "product": "Benylin Chesty Cough"}
                        }
                    },
                    "no": {
                        "question": "Is the cough dry and tickly?",
                        "yes": {
                            "question": "Do you have a sore or irritated throat?",
                            "yes": {"conclusion": "Possible dry cough with throat irritation.",
                                    "product": "Covonia Dry Cough"},
                            "no":  {"conclusion": "Possible dry cough.",
                                    "product": "Benylin Dry Cough"}
                        },
                        "no": {
                            "question": "Do you have shortness of breath?",
                            "yes": {"conclusion": "Possible respiratory condition. Seek advice.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible mild respiratory irritation.",
                                    "product": "Throat Lozenges"}
                        }
                    }
                },
                "no": {
                    "question": "Do you have a blocked or runny nose?",
                    "yes": {
                        "question": "Are your eyes also itchy or watery?",
                        "yes": {
                            "question": "Do symptoms worsen outdoors?",
                            "yes": {"conclusion": "Possible hay fever or allergy.",
                                    "product": "Cetirizine Antihistamine"},
                            "no":  {"conclusion": "Possible allergic rhinitis.",
                                    "product": "Beconase Nasal Spray"}
                        },
                        "no": {
                            "question": "Do you have a sore throat?",
                            "yes": {"conclusion": "Possible cold or upper respiratory infection.",
                                    "product": "Lemsip Max"},
                            "no":  {"conclusion": "Possible nasal congestion.",
                                    "product": "Sudafed Nasal Spray"}
                        }
                    },
                    "no": {
                        "question": "Do you have shortness of breath?",
                        "yes": {
                            "question": "Does it worsen with physical activity?",
                            "yes": {"conclusion": "Possible exercise-induced breathing difficulty.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible respiratory concern. Seek advice.",
                                    "product": "None — seek medical attention"}
                        },
                        "no": {
                            "question": "Do you have a sore or tight throat?",
                            "yes": {"conclusion": "Possible throat irritation.",
                                    "product": "Difflam Spray"},
                            "no":  {"conclusion": "No significant respiratory symptoms detected.",
                                    "product": "Vitamin C Tablets"}
                        }
                    }
                }
            },
            "Digestive & Stomach Issues": {
                "question": "Do you have nausea or vomiting?",
                "yes": {
                    "question": "Have you vomited more than twice today?",
                    "yes": {
                        "question": "Do you also have diarrhoea?",
                        "yes": {
                            "question": "Did symptoms start within 24 hours of eating?",
                            "yes": {"conclusion": "Possible food poisoning.",
                                    "product": "Dioralyte Rehydration Sachets"},
                            "no":  {"conclusion": "Possible gastroenteritis.",
                                    "product": "Dioralyte Rehydration Sachets"}
                        },
                        "no": {
                            "question": "Do you have stomach cramps?",
                            "yes": {"conclusion": "Possible stomach bug.",
                                    "product": "Buscopan"},
                            "no":  {"conclusion": "Possible nausea-dominant illness.",
                                    "product": "Motilium Anti-Nausea"}
                        }
                    },
                    "no": {
                        "question": "Do you feel bloated or gassy?",
                        "yes": {
                            "question": "Does it worsen after eating?",
                            "yes": {"conclusion": "Possible indigestion or IBS.",
                                    "product": "Rennie Deflatine"},
                            "no":  {"conclusion": "Possible trapped wind.",
                                    "product": "Windsetlers Tablets"}
                        },
                        "no": {
                            "question": "Do you have heartburn or acid reflux?",
                            "yes": {"conclusion": "Possible acid reflux.",
                                    "product": "Gaviscon Advance"},
                            "no":  {"conclusion": "Possible mild nausea.",
                                    "product": "Motilium Anti-Nausea"}
                        }
                    }
                },
                "no": {
                    "question": "Do you have stomach pain or cramps?",
                    "yes": {
                        "question": "Does the pain come and go?",
                        "yes": {
                            "question": "Is the pain severe?",
                            "yes": {"conclusion": "Severe abdominal pain — seek medical attention.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible cramps or spasms.",
                                    "product": "Buscopan"}
                        },
                        "no": {
                            "question": "Does the pain worsen after eating?",
                            "yes": {"conclusion": "Possible indigestion.",
                                    "product": "Gaviscon Advance"},
                            "no":  {"conclusion": "Possible mild stomach discomfort.",
                                    "product": "Peppermint Oil Capsules"}
                        }
                    },
                    "no": {
                        "question": "Do you have constipation or diarrhoea?",
                        "yes": {
                            "question": "Have symptoms lasted more than 3 days?",
                            "yes": {"conclusion": "Possible bowel condition. See a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible short-term bowel disruption.",
                                    "product": "Imodium"}
                        },
                        "no": {
                            "question": "Do you have heartburn?",
                            "yes": {"conclusion": "Possible acid reflux.",
                                    "product": "Gaviscon Advance"},
                            "no":  {"conclusion": "No significant digestive symptoms detected.",
                                    "product": "Peppermint Oil Capsules"}
                        }
                    }
                }
            },
            "Skin, Allergies & Reactions": {
                "question": "Do you have a visible rash or skin irritation?",
                "yes": {
                    "question": "Is the rash itchy?",
                    "yes": {
                        "question": "Did the rash appear after contact with something new?",
                        "yes": {
                            "question": "Is the rash spreading?",
                            "yes": {"conclusion": "Possible allergic contact reaction.",
                                    "product": "Hydrocortisone Cream"},
                            "no":  {"conclusion": "Possible localised contact dermatitis.",
                                    "product": "Hydrocortisone Cream"}
                        },
                        "no": {
                            "question": "Is the rash in patches or all over?",
                            "yes": {"conclusion": "Possible eczema or psoriasis.",
                                    "product": "E45 Cream"},
                            "no":  {"conclusion": "Possible hives or urticaria.",
                                    "product": "Cetirizine Antihistamine"}
                        }
                    },
                    "no": {
                        "question": "Is the skin dry or flaky?",
                        "yes": {
                            "question": "Is the skin cracked or bleeding?",
                            "yes": {"conclusion": "Possible severe dry skin condition.",
                                    "product": "Aveeno Moisturising Cream"},
                            "no":  {"conclusion": "Possible dry skin or mild eczema.",
                                    "product": "E45 Cream"}
                        },
                        "no": {
                            "question": "Is there swelling alongside the rash?",
                            "yes": {"conclusion": "Possible inflammatory skin reaction.",
                                    "product": "Hydrocortisone Cream"},
                            "no":  {"conclusion": "Possible mild skin irritation.",
                                    "product": "Sudocrem"}
                        }
                    }
                },
                "no": {
                    "question": "Do you have itchy or watery eyes?",
                    "yes": {
                        "question": "Do you also have a runny nose?",
                        "yes": {
                            "question": "Are symptoms worse outdoors?",
                            "yes": {"conclusion": "Possible hay fever.",
                                    "product": "Cetirizine Antihistamine"},
                            "no":  {"conclusion": "Possible perennial allergic rhinitis.",
                                    "product": "Beconase Nasal Spray"}
                        },
                        "no": {
                            "question": "Are your eyes red or sore?",
                            "yes": {"conclusion": "Possible allergic conjunctivitis.",
                                    "product": "Opticrom Eye Drops"},
                            "no":  {"conclusion": "Possible mild eye irritation.",
                                    "product": "Optrex Eye Drops"}
                        }
                    },
                    "no": {
                        "question": "Do you have swelling anywhere on your body?",
                        "yes": {
                            "question": "Did the swelling appear suddenly?",
                            "yes": {"conclusion": "Possible allergic reaction. Seek advice.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "Possible mild inflammatory response.",
                                    "product": "Ibuprofen Tablets"}
                        },
                        "no": {
                            "question": "Do you have sneezing fits?",
                            "yes": {"conclusion": "Possible allergic reaction.",
                                    "product": "Cetirizine Antihistamine"},
                            "no":  {"conclusion": "No significant allergy symptoms detected.",
                                    "product": "Cetirizine Antihistamine"}
                        }
                    }
                }
            },
            "Energy, Sleep & Wellbeing": {
                "question": "Are you feeling unusually tired or fatigued?",
                "yes": {
                    "question": "Have you been sleeping less than usual?",
                    "yes": {
                        "question": "Do you have difficulty falling asleep?",
                        "yes": {
                            "question": "Do you feel anxious at bedtime?",
                            "yes": {"conclusion": "Possible anxiety-related insomnia.",
                                    "product": "Nytol Herbal Tablets"},
                            "no":  {"conclusion": "Possible sleep onset difficulty.",
                                    "product": "Nytol One-A-Night"}
                        },
                        "no": {
                            "question": "Do you wake frequently during the night?",
                            "yes": {"conclusion": "Possible disrupted sleep pattern.",
                                    "product": "Nytol One-A-Night"},
                            "no":  {"conclusion": "Possible poor sleep quality.",
                                    "product": "Kalms Night Tablets"}
                        }
                    },
                    "no": {
                        "question": "Do you feel tired even after a full night of sleep?",
                        "yes": {
                            "question": "Do you also feel low in mood?",
                            "yes": {"conclusion": "Possible low mood and fatigue.",
                                    "product": "Vitamin B Complex"},
                            "no":  {"conclusion": "Possible fatigue without mood changes.",
                                    "product": "Vitamin B Complex"}
                        },
                        "no": {
                            "question": "Have you recently had an illness?",
                            "yes": {"conclusion": "Possible post-illness fatigue.",
                                    "product": "Vitamin C Tablets"},
                            "no":  {"conclusion": "Possible general tiredness.",
                                    "product": "Iron Supplement"}
                        }
                    }
                },
                "no": {
                    "question": "Are you feeling dizzy or lightheaded?",
                    "yes": {
                        "question": "Does the dizziness occur when standing up?",
                        "yes": {
                            "question": "Do you also feel faint?",
                            "yes": {"conclusion": "Possible postural hypotension. See a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible mild postural dizziness.",
                                    "product": "Iron Supplement"}
                        },
                        "no": {
                            "question": "Do you feel nauseous alongside the dizziness?",
                            "yes": {"conclusion": "Possible inner ear issue or vertigo.",
                                    "product": "Stugeron Vertigo Tablets"},
                            "no":  {"conclusion": "Possible mild dizziness.",
                                    "product": "Vitamin B Complex"}
                        }
                    },
                    "no": {
                        "question": "Are you feeling low in mood or lacking motivation?",
                        "yes": {
                            "question": "Have these feelings persisted for more than 2 weeks?",
                            "yes": {"conclusion": "Possible low mood. Consider speaking to a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible temporary low mood.",
                                    "product": "Vitamin D Supplement"}
                        },
                        "no": {
                            "question": "Do you feel generally unwell without a clear cause?",
                            "yes": {"conclusion": "Possible general malaise.",
                                    "product": "Vitamin C Tablets"},
                            "no":  {"conclusion": "No significant wellbeing concerns detected.",
                                    "product": "Vitamin B Complex"}
                        }
                    }
                }
            },
            "Mental Health & Cognitive Issues": {
                "question": "Are you feeling anxious or stressed?",
                "yes": {
                    "question": "Is the anxiety affecting your daily life?",
                    "yes": {
                        "question": "Do you have physical symptoms such as a racing heart?",
                        "yes": {
                            "question": "Have these symptoms lasted more than 2 weeks?",
                            "yes": {"conclusion": "Possible anxiety disorder. Please see a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible acute anxiety episode.",
                                    "product": "Kalms Day Tablets"}
                        },
                        "no": {
                            "question": "Do you have difficulty sleeping due to anxiety?",
                            "yes": {"conclusion": "Possible anxiety-related insomnia.",
                                    "product": "Nytol Herbal Tablets"},
                            "no":  {"conclusion": "Possible stress and anxiety.",
                                    "product": "Kalms Day Tablets"}
                        }
                    },
                    "no": {
                        "question": "Do you feel overwhelmed or unable to concentrate?",
                        "yes": {
                            "question": "Is this related to a specific situation?",
                            "yes": {"conclusion": "Possible situational stress.",
                                    "product": "Kalms Day Tablets"},
                            "no":  {"conclusion": "Possible generalised stress.",
                                    "product": "Kalms Day Tablets"}
                        },
                        "no": {
                            "question": "Do you feel irritable or on edge?",
                            "yes": {"conclusion": "Possible mild stress response.",
                                    "product": "Kalms Day Tablets"},
                            "no":  {"conclusion": "Possible mild anxiety.",
                                    "product": "Kalms Day Tablets"}
                        }
                    }
                },
                "no": {
                    "question": "Are you having difficulty concentrating or remembering things?",
                    "yes": {
                        "question": "Have you been sleeping poorly?",
                        "yes": {
                            "question": "Do you also feel fatigued?",
                            "yes": {"conclusion": "Possible fatigue-related cognitive difficulty.",
                                    "product": "Vitamin B Complex"},
                            "no":  {"conclusion": "Possible sleep-related concentration issues.",
                                    "product": "Nytol One-A-Night"}
                        },
                        "no": {
                            "question": "Have these issues come on suddenly?",
                            "yes": {"conclusion": "Sudden cognitive changes — see a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible mild cognitive difficulty.",
                                    "product": "Vitamin B Complex"}
                        }
                    },
                    "no": {
                        "question": "Are you feeling low or hopeless?",
                        "yes": {
                            "question": "Have these feelings lasted more than 2 weeks?",
                            "yes": {"conclusion": "Possible depression. Please see a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible temporary low mood.",
                                    "product": "Vitamin D Supplement"}
                        },
                        "no": {
                            "question": "Do you feel emotionally numb or detached?",
                            "yes": {"conclusion": "Possible emotional difficulty. Consider speaking to a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "No significant mental health concerns detected.",
                                    "product": "Vitamin B Complex"}
                        }
                    }
                }
            },
            "Urgent or Concerning Symptoms": {
                "question": "Do you have chest pain or tightness?",
                "yes": {
                    "question": "Is the pain spreading to your arm, jaw or back?",
                    "yes": {
                        "question": "Did the pain come on suddenly?",
                        "yes": {
                            "question": "Are you also sweating or feeling faint?",
                            "yes": {"conclusion": "Possible cardiac emergency. Call 999 immediately.",
                                    "product": "None — call 999 immediately"},
                            "no":  {"conclusion": "Possible cardiac event. Seek urgent medical attention.",
                                    "product": "None — seek medical attention"}
                        },
                        "no": {
                            "question": "Do you have a history of heart problems?",
                            "yes": {"conclusion": "Possible cardiac concern. See a GP urgently.",
                                    "product": "None — see a GP urgently"},
                            "no":  {"conclusion": "Possible musculoskeletal chest pain.",
                                    "product": "Ibuprofen Tablets"}
                        }
                    },
                    "no": {
                        "question": "Is the pain worse when breathing in?",
                        "yes": {
                            "question": "Do you also have a cough?",
                            "yes": {"conclusion": "Possible pleurisy or chest infection. See a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible respiratory concern. Seek advice.",
                                    "product": "None — seek medical attention"}
                        },
                        "no": {
                            "question": "Does the pain ease with antacids?",
                            "yes": {"conclusion": "Possible acid reflux or indigestion.",
                                    "product": "Gaviscon Advance"},
                            "no":  {"conclusion": "Possible musculoskeletal chest discomfort.",
                                    "product": "Ibuprofen Tablets"}
                        }
                    }
                },
                "no": {
                    "question": "Do you have difficulty breathing?",
                    "yes": {
                        "question": "Did the breathing difficulty come on suddenly?",
                        "yes": {
                            "question": "Do you have a known respiratory condition?",
                            "yes": {"conclusion": "Possible flare-up. Use prescribed medication and seek advice.",
                                    "product": "None — use prescribed medication"},
                            "no":  {"conclusion": "Sudden breathing difficulty — seek urgent attention.",
                                    "product": "None — seek medical attention"}
                        },
                        "no": {
                            "question": "Is the difficulty mild and worsening gradually?",
                            "yes": {"conclusion": "Possible developing respiratory condition. See a GP.",
                                    "product": "None — see a GP"},
                            "no":  {"conclusion": "Possible mild breathing difficulty.",
                                    "product": "None — seek medical attention"}
                        }
                    },
                    "no": {
                        "question": "Do you have a sudden severe headache?",
                        "yes": {
                            "question": "Is it the worst headache you have ever had?",
                            "yes": {"conclusion": "Possible serious neurological event. Call 999.",
                                    "product": "None — call 999 immediately"},
                            "no":  {"conclusion": "Possible severe headache. Seek medical advice.",
                                    "product": "Paracetamol"}
                        },
                        "no": {
                            "question": "Do you have any other rapidly worsening symptoms?",
                            "yes": {"conclusion": "Rapidly worsening symptoms — seek medical attention.",
                                    "product": "None — seek medical attention"},
                            "no":  {"conclusion": "No urgent symptoms detected at this time.",
                                    "product": "Paracetamol"}
                        }
                    }
                }
            }
        }

        self.currentNode      = None
        self.selectedCategory = None
        self.bgQuestionIndex  = 0
        self.questionDepth    = 0

        self._buildUI()

    def _buildUI(self):
        titleBar, self.toggleBtn = buildTitleBar(self, self.controller)

        ctk.CTkButton(self, text="← Home", width=90, height=30,
                      fg_color="transparent",
                      hover_color=("#E0E0E0", "#333333"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=12),
                      corner_radius=8,
                      command=lambda: self.controller.showFrame("HomeFrame")).place(x=10, y=90)

        self.backBtn = ctk.CTkButton(self, text="← Back", width=90, height=30,
                                      fg_color="transparent",
                                      hover_color=("#E0E0E0", "#333333"),
                                      text_color=("black", "white"),
                                      font=ctk.CTkFont(size=12),
                                      corner_radius=8,
                                      command=self.showDisclaimer)
        self.backBtn.place(x=110, y=90)

        self.contentFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.contentFrame.pack(expand=True, fill="both", padx=60, pady=(40, 0))

        ctk.CTkLabel(
            self,
            text="Your data is securely stored and kept private. Not associated with NHS systems.",
            font=ctk.CTkFont(size=11),
            text_color="gray").pack(side="bottom", pady=(0, 10))

        self.showDisclaimer()

    def _clearContent(self):
        for widget in self.contentFrame.winfo_children():
            widget.destroy()

    def showDisclaimer(self):
        self.backBtn.configure(command=lambda: self.controller.showFrame("HomeFrame"))
        self._clearContent()

        ctk.CTkLabel(self.contentFrame, text="Diagnosis Tool",
                     font=ctk.CTkFont("Segoe UI", 28, "bold")).pack(pady=(20, 24))

        disclaimerText1 = (
            "This diagnosis tool provides general guidance based on the symptoms you select. "
            "It is not a medical diagnosis and should not be used as a substitute for "
            "professional healthcare advice."
        )
        disclaimerText2 = (
            "If your symptoms become severe, do not improve, or you are unsure about your "
            "condition, you should contact a pharmacist, GP, or another qualified healthcare "
            "professional."
        )
        disclaimerText3 = (
            "By continuing, you agree to use this tool responsibly and understand that the "
            "information provided is for basic support only."
        )

        for text in (disclaimerText1, disclaimerText2, disclaimerText3):
            ctk.CTkLabel(self.contentFrame, text=text,
                         font=ctk.CTkFont(size=13),
                         wraplength=700,
                         justify="center").pack(pady=(0, 16))

        ctk.CTkButton(self.contentFrame, text="Begin Background\nCheck",
                      width=200, height=60,
                      fg_color=GREEN_PRIMARY, hover_color=GREEN_HOVER,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=16,
                      command=self.startBackgroundCheck).pack(pady=(16, 0))

    def startBackgroundCheck(self):
        self.bgQuestionIndex = 0
        self.showBackgroundQuestion()

    def showBackgroundQuestion(self):
        self.backBtn.configure(command=self.showDisclaimer)
        self._clearContent()

        if self.bgQuestionIndex >= len(self.bgQuestions):
            self.showCategorySelection()
            return

        question, referralAnswer = self.bgQuestions[self.bgQuestionIndex]

        ctk.CTkLabel(self.contentFrame, text="Background Check",
                     font=ctk.CTkFont("Segoe UI", 24, "bold")).pack(pady=(20, 8))

        ctk.CTkLabel(self.contentFrame,
                     text=f"Question {self.bgQuestionIndex + 1} of {len(self.bgQuestions)}",
                     font=ctk.CTkFont(size=12),
                     text_color="gray").pack(pady=(0, 24))

        ctk.CTkLabel(self.contentFrame, text=question,
                     font=ctk.CTkFont(size=16),
                     wraplength=600,
                     justify="center").pack(pady=(0, 32))

        btnRow = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        btnRow.pack()

        ctk.CTkButton(btnRow, text="Yes", width=140, height=48,
                      fg_color=BLUE_PRIMARY, hover_color=BLUE_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.handleBgAnswer("yes", referralAnswer)).pack(
                          side="left", padx=16)

        ctk.CTkButton(btnRow, text="No", width=140, height=48,
                      fg_color=("#6B6B6B", "#4A4A4A"),
                      hover_color=("#555555", "#3A3A3A"),
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.handleBgAnswer("no", referralAnswer)).pack(
                          side="left", padx=16)

    def handleBgAnswer(self, answer, referralAnswer):
        if answer == referralAnswer:
            self.referUser()
        else:
            self.nextBackgroundQuestion()

    def nextBackgroundQuestion(self):
        self.bgQuestionIndex += 1
        self.showBackgroundQuestion()

    def referUser(self):
        self.backBtn.configure(command=self.showDisclaimer)
        self._clearContent()

        ctk.CTkLabel(self.contentFrame, text="Please Seek Professional Advice",
                     font=ctk.CTkFont("Segoe UI", 24, "bold"),
                     text_color="#E53935").pack(pady=(20, 24))

        ctk.CTkLabel(self.contentFrame,
                     text="Based on your answers, we recommend that you consult a pharmacist, "
                          "GP, or another qualified healthcare professional before using this tool. "
                          "Please do not delay seeking medical advice.",
                     font=ctk.CTkFont(size=14),
                     wraplength=640,
                     justify="center").pack(pady=(0, 32))

        ctk.CTkButton(self.contentFrame, text="Return to Home",
                      width=200, height=48,
                      fg_color=RED_LOGOUT, hover_color=RED_LOGOUT_HOV,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.controller.showFrame("HomeFrame")).pack()

    def showCategorySelection(self):
        self.backBtn.configure(command=self.showDisclaimer)
        self._clearContent()

        ctk.CTkLabel(self.contentFrame, text="Diagnosis Tool",
                     font=ctk.CTkFont("Segoe UI", 24, "bold")).pack(pady=(10, 2))

        ctk.CTkLabel(self.contentFrame,
                     text="Select a category that best matches your symptoms.",
                     font=ctk.CTkFont("Segoe UI", 14),
                     text_color="gray").pack(pady=(0, 16))

        categoryData = [
            {"title": "Pain & Discomfort",
             "description": "For aches, pains, or ongoing physical discomfort.",
             "icon": "🤕",
             "command": lambda c="Pain & Discomfort": self.startDiagnosis(c)},
            {"title": "Temperature &\nInfection Signs",
             "description": "For fever, chills, or signs of infection.",
             "icon": "🌡️",
             "command": lambda c="Temperature & Infection Signs": self.startDiagnosis(c)},
            {"title": "Respiratory\nSymptoms",
             "description": "For breathing difficulty or throat problems.",
             "icon": "🫁",
             "command": lambda c="Respiratory Symptoms": self.startDiagnosis(c)},
            {"title": "Digestive &\nStomach Issues",
             "description": "For nausea, stomach pain or bowel problems.",
             "icon": "🫀",
             "command": lambda c="Digestive & Stomach Issues": self.startDiagnosis(c)},
            {"title": "Skin, Allergies\n& Reactions",
             "description": "For rashes, itching, swelling or allergic reactions.",
             "icon": "🧴",
             "command": lambda c="Skin, Allergies & Reactions": self.startDiagnosis(c)},
            {"title": "Energy, Sleep\n& Wellbeing",
             "description": "For tiredness, dizziness or sleep-related issues.",
             "icon": "😴",
             "command": lambda c="Energy, Sleep & Wellbeing": self.startDiagnosis(c)},
            {"title": "Mental Health &\nCognitive Issues",
             "description": "For stress, anxiety or changes in mood or focus.",
             "icon": "🧠",
             "command": lambda c="Mental Health & Cognitive Issues": self.startDiagnosis(c)},
            {"title": "Urgent or\nConcerning Symptoms",
             "description": "For severe or rapidly worsening symptoms.",
             "icon": "⚠️",
             "command": lambda c="Urgent or Concerning Symptoms": self.startDiagnosis(c)},
        ]

        gridFrame = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        gridFrame.pack(expand=True, fill="both", padx=20, pady=(0, 8))

        for col in range(4):
            gridFrame.grid_columnconfigure(col, weight=1, uniform="cat")
        gridFrame.grid_rowconfigure((0, 1), weight=1)

        for index, data in enumerate(categoryData):
            row = index // 4
            col = index % 4
            card = self._makeCategoryCard(gridFrame, **data)
            card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        ctk.CTkButton(self.contentFrame,
                      text="Can't find your category?",
                      width=240, height=38,
                      fg_color="transparent",
                      border_width=1,
                      border_color=("#A0A0A0", "#555555"),
                      text_color=("black", "white"),
                      hover_color=("#E0E0E0", "#333333"),
                      font=ctk.CTkFont(size=13),
                      corner_radius=20,
                      command=self.showCantFindMessage).pack(pady=(4, 8))

    def showCantFindMessage(self):
        self._clearContent()
        self.backBtn.configure(command=self.showCategorySelection)

        ctk.CTkLabel(self.contentFrame, text="Diagnosis Tool",
                     font=ctk.CTkFont("Segoe UI", 24, "bold")).pack(pady=(20, 4))

        ctk.CTkLabel(self.contentFrame,
                     text="Can't find your category?",
                     font=ctk.CTkFont("Segoe UI", 16, "bold")).pack(pady=(20, 4))

        ctk.CTkLabel(self.contentFrame,
                     text="Try to identify your most prominent symptom and select the "
                          "category that most closely matches it. For example:\n\n"
                          "• A high temperature or feeling hot → Temperature & Infection Signs\n"
                          "• A cough, blocked nose or sore throat → Respiratory Symptoms\n"
                          "• Stomach pain, nausea or bowel issues → Digestive & Stomach Issues\n"
                          "• Feeling anxious, low or struggling to concentrate → Mental Health & Cognitive Issues\n"
                          "• A rash, itching or swelling → Skin, Allergies & Reactions\n\n"
                          "If your symptoms feel severe or are worsening rapidly, please select "
                          "Urgent or Concerning Symptoms or seek medical attention immediately.",
                     font=ctk.CTkFont(size=13),
                     wraplength=680,
                     justify="left").pack(padx=40, pady=(8, 24))

        ctk.CTkButton(self.contentFrame, text="Back to Categories",
                      width=200, height=44,
                      fg_color=BLUE_PRIMARY, hover_color=BLUE_DARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=12,
                      command=self.showCategorySelection).pack()

    def _makeCategoryCard(self, parent, title, description, icon, command):
        card = ctk.CTkFrame(parent, corner_radius=14,
                             fg_color=("#1A2B4A", "#1A2B4A"))

        ctk.CTkLabel(card, text=icon,
                     font=ctk.CTkFont(size=28)).pack(pady=(14, 2))
        ctk.CTkLabel(card, text=title,
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color="white",
                     justify="center").pack(padx=8, pady=(0, 4))
        ctk.CTkLabel(card, text=description,
                     font=ctk.CTkFont(size=10),
                     text_color="#A0B0C8",
                     justify="center",
                     wraplength=160).pack(padx=8, pady=(0, 14))

        card.bind("<Enter>", lambda e: card.configure(fg_color="#243660"))
        card.bind("<Leave>", lambda e: card.configure(fg_color="#1A2B4A"))

        if command:
            card.bind("<Button-1>", lambda e: command())
            for widget in card.winfo_children():
                widget.bind("<Button-1>", lambda e: command())

        return card

    def startDiagnosis(self, category):
        self.selectedCategory = category
        self.currentNode = self.diagnosisTrees[category]
        self.questionDepth = 0
        self.showDiagnosisQuestion()

    def showDiagnosisQuestion(self):
        self.backBtn.configure(command=self.showCategorySelection)
        self._clearContent()

        if "conclusion" in self.currentNode:
            self.showResults()
            return

        question = self.currentNode["question"]

        ctk.CTkLabel(self.contentFrame, text=self.selectedCategory,
                     font=ctk.CTkFont("Segoe UI", 22, "bold")).pack(pady=(20, 4))

        progress = min(self.questionDepth / 4, 1.0)
        progressBar = ctk.CTkProgressBar(self.contentFrame, width=400,
                                          fg_color=("#D0D8E8", "#2A2A4A"),
                                          progress_color=BLUE_PRIMARY)
        progressBar.pack(pady=(0, 16))
        progressBar.set(progress)

        ctk.CTkLabel(self.contentFrame, text=question,
                     font=ctk.CTkFont(size=16),
                     wraplength=640,
                     justify="center").pack(pady=(24, 32))

        btnRow = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        btnRow.pack()

        ctk.CTkButton(btnRow, text="Yes", width=140, height=48,
                      fg_color=BLUE_PRIMARY, hover_color=BLUE_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.handleDiagnosisAnswer("yes")).pack(
                          side="left", padx=16)

        ctk.CTkButton(btnRow, text="No", width=140, height=48,
                      fg_color=("#6B6B6B", "#4A4A4A"),
                      hover_color=("#555555", "#3A3A3A"),
                      font=ctk.CTkFont(size=14, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.handleDiagnosisAnswer("no")).pack(
                          side="left", padx=16)

    def handleDiagnosisAnswer(self, answer):
        if answer == "yes":
            self.currentNode = self.currentNode["yes"]
        else:
            self.currentNode = self.currentNode["no"]
        self.questionDepth += 1
        self.showDiagnosisQuestion()

    def showResults(self):
        self.backBtn.configure(command=self.showCategorySelection)
        self._clearContent()

        conclusion = self.currentNode["conclusion"]
        product    = self.currentNode["product"]

        ctk.CTkLabel(self.contentFrame, text="Your Results",
                     font=ctk.CTkFont("Segoe UI", 26, "bold")).pack(pady=(20, 4))

        ctk.CTkLabel(self.contentFrame, text=self.selectedCategory,
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color="gray").pack(pady=(0, 20))

        conclusionCard = ctk.CTkFrame(self.contentFrame, corner_radius=14,
                                       fg_color=("#EEF2FF", "#1E2A45"))
        conclusionCard.pack(fill="x", padx=40, pady=(0, 16))

        ctk.CTkLabel(conclusionCard, text="Diagnosis",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=BLUE_PRIMARY).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(conclusionCard, text=conclusion,
                     font=ctk.CTkFont(size=14),
                     wraplength=680,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 14))

        productCard = ctk.CTkFrame(self.contentFrame, corner_radius=14,
                                    fg_color=("#F0FFF4", "#1A3A2A"))
        productCard.pack(fill="x", padx=40, pady=(0, 24))

        ctk.CTkLabel(productCard, text="Recommended Product",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=GREEN_PRIMARY).pack(anchor="w", padx=20, pady=(14, 4))
        ctk.CTkLabel(productCard, text=product,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     wraplength=680,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 14))

        btnRow = ctk.CTkFrame(self.contentFrame, fg_color="transparent")
        btnRow.pack(pady=(0, 12))

        ctk.CTkButton(btnRow, text="View in Catalogue", width=200, height=44,
                      fg_color=BLUE_PRIMARY, hover_color=BLUE_DARK,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=12,
                      command=self.controller.openCataloguePage).pack(
                          side="left", padx=12)

        ctk.CTkButton(btnRow, text="Return to Home", width=200, height=44,
                      fg_color=RED_LOGOUT, hover_color=RED_LOGOUT_HOV,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=12,
                      command=lambda: self.controller.showFrame("HomeFrame")).pack(
                          side="left", padx=12)

        ctk.CTkLabel(self.contentFrame,
                     text="This recommendation is not a substitute for professional medical advice. "
                          "Please consult a pharmacist or GP if you are unsure.",
                     font=ctk.CTkFont(size=11),
                     text_color="gray",
                     wraplength=680,
                     justify="center").pack(pady=(0, 8))

    def refreshTheme(self):
        label  = "🌙  Dark Mode" if not self.controller.darkMode else "☀  Light Mode"
        colour = "#3A3ACA" if self.controller.darkMode else "#E8B000"
        self.toggleBtn.configure(text=label, fg_color=colour)

# ══════════════════════════════════════════════
#  Catalogue Frame
# ══════════════════════════════════════════════
class CatalogueFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller     = controller
        self.allProducts    = []
        self.photoRefs      = []
        self.activeCategory = "All"
        self.autoCompleteFrame = None
        self.currentProduct = None

        self.seedProducts()
        self._buildUI()

    def seedProducts(self):
        from dbManager import getConnection
        connection = getConnection()
        cursor     = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products;")
        count = cursor.fetchone()[0]
        connection.close()

        if count > 0:
            return

        from dbManager import addProduct

        products = [
            ("Paracetamol 500mg Tablets",
             "Effective pain and fever relief suitable for headaches, colds and general aches.",
             "Take 1-2 tablets every 4-6 hours. Max 8 tablets in 24 hours.",
             1.99, "Pain Relief", "images/paracetamol.jpeg"),
            ("Ibuprofen 200mg Tablets",
             "Anti-inflammatory pain relief for headaches, dental pain, period pain and fever.",
             "Take 1-2 tablets every 4-6 hours with food. Max 6 tablets in 24 hours.",
             2.49, "Pain Relief", "images/ibuprofenTablets.jpeg"),
            ("Ibuprofen 10% Gel 50g",
             "Topical anti-inflammatory gel for localised muscle and joint pain.",
             "Apply to affected area up to 3 times daily. Do not use on broken skin.",
             4.99, "Pain Relief", "images/ibuprofenGel.jpeg"),
            ("Co-Codamol 8mg/500mg Tablets",
             "Combined paracetamol and codeine for moderate pain relief. Contains opioid.",
             "Take 1-2 tablets every 6 hours. Max 8 tablets in 24 hours. Max 3 days use.",
             3.99, "Pain Relief", "images/coCodamol.jpeg"),
            ("Deep Heat Muscle Rescue Spray",
             "Heat therapy spray for relief of tight, tense muscles and minor sports injuries.",
             "Spray onto affected area from 15cm distance. Repeat up to 3 times daily.",
             6.49, "Pain Relief", "images/deepHeatSpray.jpeg"),
            ("Sumatriptan 50mg Tablets",
             "Prescription-strength migraine treatment for moderate to severe migraine attacks.",
             "Take 1 tablet at onset of migraine. May repeat after 2 hours if needed.",
             8.99, "Pain Relief", "images/sumatriptan.jpeg"),
            ("Lemsip Max Day & Night Capsules",
             "Dual-action cold and flu relief with day and night capsules for 24-hour coverage.",
             "Take 1 yellow capsule every 6 hours (day). Take 1 blue capsule at night.",
             5.99, "Cold, Flu & Fever", "images/lemsipMax.jpeg"),
            ("Solgar Vitamin B-Complex Capsules",
             "High potency B vitamin complex to support energy levels and reduce tiredness.",
             "Take 1 capsule daily with a meal.",
             14.99, "Cold, Flu & Fever", "images/vitaminBComplex.jpeg"),
            ("Vitamin C 500mg Chewable Tablets",
             "Buffered vitamin C with rosehip and acerola to support immune function.",
             "Chew 1 tablet daily with food.",
             6.99, "Cold, Flu & Fever", "images/vitaminCTabs.jpeg"),
            ("Strepsils Sore Throat Lozenges",
             "Soothing lozenges for effective relief from sore throat and cough symptoms.",
             "Dissolve 1 lozenge in the mouth every 2-3 hours. Max 12 lozenges in 24 hours.",
             3.49, "Throat & Cough", "images/throatLozenges.jpeg"),
            ("Difflam Throat Spray 30ml",
             "Anti-inflammatory throat spray for painful and sore mouth and throat conditions.",
             "Spray 4-8 times into the throat every 1.5-3 hours as required.",
             7.49, "Throat & Cough", "images/difflamSpray.jpeg"),
            ("Benylin Chesty Coughs 150ml",
             "Non-drowsy syrup that helps loosen and clear chesty cough and chest congestion.",
             "Take 10ml up to 4 times daily. Do not exceed stated dose.",
             5.99, "Throat & Cough", "images/benylinChestyCough.jpeg"),
            ("Benylin Dry Cough Syrup",
             "Effective relief for dry, tickly and irritating coughs.",
             "Take 10ml up to 4 times daily. Do not exceed stated dose.",
             5.99, "Throat & Cough", "images/benylinDryCough.jpeg"),
            ("Covonia Dry & Tickly Cough 300ml",
             "Non-drowsy linctus for the relief of dry and tickly coughs.",
             "Take 10ml 3-4 times daily. Do not exceed stated dose.",
             4.99, "Throat & Cough", "images/covoniaDryCough.jpeg"),
            ("Zirtek Cetirizine Allergy Tablets",
             "24-hour non-drowsy antihistamine for hayfever and other allergic reactions.",
             "Take 1 tablet daily. Can be taken with or without food.",
             5.49, "Allergy & Hayfever", "images/cetirizineAntihistamine.webp"),
            ("Piriton Allergy Tablets",
             "Fast-acting antihistamine for skin allergies, hayfever, pet and food allergies.",
             "Take 1 tablet every 4-6 hours. Max 6 tablets in 24 hours.",
             3.99, "Allergy & Hayfever", "images/piritonAllergyTablets.webp"),
            ("Beconase Nasal Spray",
             "Corticosteroid nasal spray for hayfever and perennial allergic rhinitis.",
             "2 sprays into each nostril twice daily. For adults and children over 18.",
             6.99, "Allergy & Hayfever", "images/beconaseNasalSpray.jpeg"),
            ("Opticrom Allergy Eye Drops 10ml",
             "Sodium cromoglicate eye drops to prevent and relieve itchy, watery allergic eyes.",
             "Instil 1-2 drops into each eye 4 times daily.",
             6.49, "Allergy & Hayfever", "images/opticromEyeDrops.jpeg"),
            ("Optrex Allergy Eye Drops",
             "Soothes and prevents itchy, allergy-related eye symptoms.",
             "Instil 1-2 drops into each eye up to 4 times daily.",
             5.99, "Allergy & Hayfever", "images/optrexEyeDrops.jpeg"),
            ("Sudafed Blocked Nose Spray",
             "Fast-acting xylometazoline nasal spray for rapid relief of nasal congestion.",
             "1-2 sprays per nostril up to 3 times daily. Do not use for more than 7 days.",
             4.99, "Nasal & Respiratory", "images/sudafedNoseSpray.jpeg"),
            ("Sudafed Decongestant Tablets",
             "Non-drowsy pseudoephedrine tablets to unblock nasal congestion and catarrh.",
             "Take 1 tablet every 4-6 hours. Max 4 tablets in 24 hours.",
             4.49, "Nasal & Respiratory", "images/sudafedTablets.jpeg"),
            ("Sterimar Breathe Easy Spray",
             "100% natural isotonic sea water nasal spray for daily nasal hygiene.",
             "Spray 1-2 times into each nostril as required throughout the day.",
             6.99, "Nasal & Respiratory", "images/sterimar1NasalSpray.jpeg"),
            ("Sterimar Congestion Relief Spray",
             "Hypertonic sea water nasal spray for relief of nasal congestion.",
             "Spray 1-2 times into each nostril up to 6 times daily.",
             7.49, "Nasal & Respiratory", "images/sterimar2NasalSpray.jpeg"),
            ("Gaviscon Advance Tablets",
             "Chewable antacid tablets for fast relief of heartburn and acid indigestion.",
             "Chew 2-4 tablets after meals and at bedtime. Max 16 tablets daily.",
             5.49, "Digestive", "images/gavisconAdv.jpeg"),
            ("Buscopan Cramps Tablets",
             "Antispasmodic tablets for relief of stomach cramps and IBS-related pain.",
             "Take 1 tablet 3 times daily. Max 3 tablets in 24 hours.",
             4.99, "Digestive", "images/buscopan.jpeg"),
            ("Motilium Anti-Nausea Tablets",
             "Domperidone tablets for relief of nausea and vomiting.",
             "Take 1 tablet up to 3 times daily before meals. Max 3 days use.",
             6.99, "Digestive", "images/motilium.jpeg"),
            ("Rennie Deflatine Tablets",
             "Sugar-free chewable tablets for relief of trapped wind, bloating and indigestion.",
             "Chew 1-2 tablets when required. Max 11 tablets in 24 hours.",
             4.49, "Digestive", "images/rennieDeflatine.jpeg"),
            ("WindSetlers Gel Caps",
             "Simeticone gel capsules for fast relief from painful trapped wind.",
             "Take 1-2 capsules after meals and at bedtime. Max 8 capsules daily.",
             3.99, "Digestive", "images/windsettlers.jpeg"),
            ("Dioralyte Rehydration Sachets",
             "Oral electrolyte sachets to replace fluids and salts lost through diarrhoea.",
             "Dissolve 1 sachet in 200ml water. Take 1 sachet after each loose bowel movement.",
             4.99, "Digestive", "images/dioralyte.jpeg"),
            ("Imodium Instant Melts",
             "Loperamide orodispersible tablets for fast on-the-go relief of diarrhoea.",
             "Place 1 tablet on tongue and allow to dissolve. Max 4 tablets in 24 hours.",
             5.49, "Digestive", "images/imodium.jpeg"),
            ("Colpermin Peppermint Oil Capsules",
             "Sustained release peppermint oil capsules for IBS relief including bloating.",
             "Take 1-2 capsules 3 times daily, 30-60 minutes before meals.",
             7.99, "Digestive", "images/colperminPeppermintOil.jpeg"),
            ("Hydrocortisone Cream 0.5%",
             "Mild corticosteroid cream for relief of mild inflammatory skin conditions.",
             "Apply thinly to affected area twice daily. For external use only. Max 1 week.",
             3.99, "Skin", "images/hydrocortisone.jpeg"),
            ("E45 Moisturising Cream",
             "Clinically proven emollient cream for dry, itchy and irritated skin conditions.",
             "Apply to affected areas as often as required.",
             6.99, "Skin", "images/e45.jpg"),
            ("Aveeno Moisturising Cream",
             "Oat-enriched moisturising cream for sensitive and dry skin.",
             "Apply to skin as often as needed. Suitable for daily use.",
             8.99, "Skin", "images/aveenoCream.jpeg"),
            ("Sudocrem Antiseptic Cream 250g",
             "Antiseptic healing cream for nappy rash, eczema, acne and surface wounds.",
             "Apply a thin layer to the affected area and rub in gently.",
             4.99, "Skin", "images/sudocrem.jpeg"),
            ("Nytol Herbal Sleep Tablets",
             "Traditional herbal tablets with valerian, hops and passion flower for sleep.",
             "Take 2 tablets one hour before bedtime.",
             6.49, "Sleep & Wellbeing", "images/nytolHerbal.jpeg"),
            ("Nytol One-A-Night 50mg",
             "Clinically proven diphenhydramine sleep aid for a full night's sleep.",
             "Take 1 tablet 20 minutes before bedtime. For adults over 16.",
             5.99, "Sleep & Wellbeing", "images/nytolOne.jpeg"),
            ("Kalms Night One-A-Night",
             "Herbal valerian root tablets for temporary relief of sleep disturbances.",
             "Take 1 tablet one hour before bedtime.",
             5.49, "Sleep & Wellbeing", "images/kalmsNight.jpeg"),
            ("Kalms Day Tablets",
             "Traditional herbal valerian tablets for temporary relief of stress symptoms.",
             "Take 1 tablet three times daily with water.",
             5.49, "Sleep & Wellbeing", "images/kalmsDay.jpeg"),
            ("Solgar Vitamin D3 4000IU Capsules",
             "High strength vitamin D3 supplement to support mood, bones and immune health.",
             "Take 1 capsule daily with a meal.",
             12.99, "Sleep & Wellbeing", "images/vitaminD3.jpeg"),
            ("Feroglobin Iron Supplement Capsules",
             "Gentle iron supplement with folic acid and vitamin B12 for tiredness and fatigue.",
             "Take 1 capsule daily with food.",
             9.99, "Sleep & Wellbeing", "images/ironSupp.jpeg"),
            ("Stugeron 15 Vertigo Tablets",
             "Cinnarizine tablets for prevention and treatment of vertigo and travel sickness.",
             "For vertigo: take 2 tablets 3 times daily. Reduce to 1 tablet 3 times daily.",
             5.99, "Sleep & Wellbeing", "images/stugeron.jpeg"),
        ]

        for p in products:
            addProduct(*p)

    def _buildUI(self):
        titleBar, self.toggleBtn = buildTitleBar(self, self.controller)

        ctk.CTkButton(self, text="← Home", width=90, height=30,
                      fg_color="transparent",
                      hover_color=("#E0E0E0", "#333333"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=12),
                      corner_radius=8,
                      command=lambda: self.controller.showFrame("HomeFrame")).place(x=10, y=90)

        self.searchFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.searchFrame.pack(fill="x", padx=60, pady=(50, 6))

        self.searchVar = ctk.StringVar()
        self.searchVar.trace("w", lambda *a: self.onSearchChange())

        self.searchEntry = ctk.CTkEntry(self.searchFrame,
                                         textvariable=self.searchVar,
                                         width=700, height=44,
                                         placeholder_text="🔍  Search for a medicine or product...",
                                         font=ctk.CTkFont(size=14),
                                         corner_radius=22)
        self.searchEntry.pack()

        self.filterFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.filterFrame.pack(fill="x", padx=60, pady=(4, 8))

        categories = [
            "All", "Pain Relief", "Cold, Flu & Fever", "Throat & Cough",
            "Allergy & Hayfever", "Nasal & Respiratory", "Digestive",
            "Skin", "Sleep & Wellbeing"
        ]

        self.filterButtons = {}
        for cat in categories:
            btn = ctk.CTkButton(self.filterFrame,
                                text=cat,
                                width=0, height=30,
                                fg_color=BLUE_PRIMARY if cat == "All" else ("#E0E0E0", "#3A3A3A"),
                                hover_color=(BLUE_DARK, "#2A2A6A"),
                                text_color="white" if cat == "All" else ("black", "white"),
                                font=ctk.CTkFont(size=11),
                                corner_radius=15,
                                command=lambda c=cat: self.filterByCategory(c))
            btn.pack(side="left", padx=3, pady=2)
            self.filterButtons[cat] = btn

        self.scrollFrame = ctk.CTkScrollableFrame(self,
                                                   fg_color="transparent",
                                                   scrollbar_button_color=BLUE_PRIMARY,
                                                   scrollbar_button_hover_color=BLUE_DARK)
        self.scrollFrame.pack(expand=True, fill="both", padx=60, pady=(0, 4))

        for col in range(4):
            self.scrollFrame.grid_columnconfigure(col, weight=1, uniform="prod")

        self.bind("<Button-1>", lambda e: self.hideAutoComplete())
        self.scrollFrame.bind("<Button-1>", lambda e: self.hideAutoComplete())
        self.filterFrame.bind("<Button-1>", lambda e: self.hideAutoComplete())

        ctk.CTkLabel(
            self,
            text="Your data is securely stored and kept private. Not associated with NHS systems.",
            font=ctk.CTkFont(size=11),
            text_color="gray").pack(side="bottom", pady=(0, 6))

    def loadProducts(self):
        from dbManager import getAllProducts
        self.allProducts = getAllProducts()
        self.displayProducts(self.allProducts)

    def displayProducts(self, products):
        for widget in self.scrollFrame.winfo_children():
            widget.destroy()
        self.photoRefs = []

        if not products:
            ctk.CTkLabel(self.scrollFrame,
                         text="No products found.",
                         font=ctk.CTkFont(size=14),
                         text_color="gray").grid(row=0, column=0, columnspan=4, pady=40)
            return

        for index, product in enumerate(products):
            row = index // 4
            col = index % 4
            card = self._makeProductCard(product)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

    def _makeProductCard(self, product):
        productId, productName, description, dosageProd, price, category, imagePath = product

        card = ctk.CTkFrame(self.scrollFrame, corner_radius=16,
                             fg_color=(CARD_LIGHT, CARD_DARK),
                             border_width=1,
                             border_color=("#D0D8E8", "#3A3A5C"))

        try:
            img   = Image.open(imagePath)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(180, 160))
            self.photoRefs.append(photo)
            ctk.CTkLabel(card, image=photo, text="").pack(pady=(12, 4))
        except Exception:
            ctk.CTkLabel(card, text="📦",
                         font=ctk.CTkFont(size=48)).pack(pady=(12, 4))

        ctk.CTkLabel(card, text=productName,
                     font=ctk.CTkFont("Segoe UI", 11, "bold"),
                     wraplength=180,
                     justify="center").pack(padx=8, pady=(4, 2))

        ctk.CTkLabel(card, text=f"£{price:.2f}",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=BLUE_PRIMARY).pack(pady=(0, 2))

        ctk.CTkLabel(card, text=description,
                     font=ctk.CTkFont(size=10),
                     text_color="gray",
                     wraplength=180,
                     justify="center").pack(padx=8, pady=(0, 12))

        card.bind("<Enter>", lambda e: card.configure(border_color=BLUE_PRIMARY))
        card.bind("<Leave>", lambda e: card.configure(border_color=("#D0D8E8", "#3A3A5C")))
        card.bind("<Button-1>", lambda e: self.showProductDetail(product))
        for widget in card.winfo_children():
            widget.bind("<Button-1>", lambda e, p=product: self.showProductDetail(p))

        return card

    def onSearchChange(self):
        query = self.searchVar.get().strip()

        if query == "":
            self.hideAutoComplete()
            self.filterByCategory(self.activeCategory)
            return

        from dbManager import searchProducts
        results = searchProducts(query)

        if self.activeCategory != "All":
            results = [p for p in results if p[5] == self.activeCategory]

        self.displayProducts(results)
        self.showAutoComplete(results)

    def filterByCategory(self, category):
        self.activeCategory = category
        for cat, btn in self.filterButtons.items():
            if cat == category:
                btn.configure(fg_color=BLUE_PRIMARY, text_color="white")
            else:
                btn.configure(fg_color=("#E0E0E0", "#3A3A3A"),
                               text_color=("black", "white"))
        if category == "All":
            self.displayProducts(self.allProducts)
        else:
            from dbManager import getProductsByCategory
            results = getProductsByCategory(category)
            self.displayProducts(results)

    def showAutoComplete(self, results):
        self.hideAutoComplete()

        suggestions = [p[1] for p in results[:5]]

        if not suggestions:
            return

        self.autoCompleteFrame = ctk.CTkFrame(self,
                                               corner_radius=12,
                                               fg_color=(CARD_LIGHT, CARD_DARK),
                                               border_width=1,
                                               border_color=("#D0D8E8", "#3A3A5C"))

        for name in suggestions:
            suggestionBtn = ctk.CTkButton(
                self.autoCompleteFrame,
                text=name,
                width=700, height=36,
                fg_color="transparent",
                hover_color=("#EEF2FF", "#2A2A4A"),
                text_color=("black", "white"),
                font=ctk.CTkFont(size=13),
                anchor="w",
                command=lambda n=name: self.selectSuggestion(n))
            suggestionBtn.pack(fill="x", padx=4, pady=2)

        self.autoCompleteFrame.place(x=60, y=188)

    def hideAutoComplete(self):
        if self.autoCompleteFrame is not None:
            self.autoCompleteFrame.destroy()
            self.autoCompleteFrame = None

    def selectSuggestion(self, productName):
        self.searchVar.set(productName)
        self.hideAutoComplete()
        from dbManager import searchProducts
        results = searchProducts(productName)
        if self.activeCategory != "All":
            results = [p for p in results if p[5] == self.activeCategory]
        self.displayProducts(results)

    def showProductDetail(self, product):
        productId, productName, description, dosageProd, price, category, imagePath = product
        self.currentProduct = product

        self.searchFrame.pack_forget()
        self.filterFrame.pack_forget()
        self.scrollFrame.pack_forget()

        self.detailFrame = ctk.CTkFrame(self, fg_color="transparent")
        self.detailFrame.pack(expand=True, fill="both", padx=60, pady=(10, 10))

        ctk.CTkButton(self.detailFrame, text="←", width=36, height=30,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=16, weight="bold"),
                      corner_radius=8,
                      command=self.hideProductDetail).pack(anchor="w", pady=(0, 16))

        contentRow = ctk.CTkFrame(self.detailFrame, fg_color="transparent")
        contentRow.pack(fill="both", expand=True)
        contentRow.grid_columnconfigure(0, weight=1)
        contentRow.grid_columnconfigure(1, weight=2)
        contentRow.grid_rowconfigure(0, weight=1)

        # Left panel
        imagePanel = ctk.CTkFrame(contentRow, corner_radius=16,
                                   fg_color=(CARD_LIGHT, CARD_DARK),
                                   border_width=1,
                                   border_color=("#D0D8E8", "#3A3A5C"))
        imagePanel.grid(row=0, column=0, padx=(0, 16), pady=8, sticky="nsew")

        try:
            img   = Image.open(imagePath)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(240, 220))
            self.photoRefs.append(photo)
            ctk.CTkLabel(imagePanel, image=photo, text="").pack(pady=20)
        except Exception:
            ctk.CTkLabel(imagePanel, text="📦",
                         font=ctk.CTkFont(size=80)).pack(pady=20)

        ctk.CTkLabel(imagePanel, text="RRP: " f"£{price:.2f}",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=BLUE_PRIMARY).pack(pady=(0, 8))

        ctk.CTkLabel(imagePanel, text=category,
                     font=ctk.CTkFont(size=12),
                     text_color="gray").pack(pady=(0, 16))

        # Right panel
        infoPanel = ctk.CTkScrollableFrame(contentRow, corner_radius=16,
                                            fg_color=(CARD_LIGHT, CARD_DARK),
                                            border_width=1,
                                            border_color=("#D0D8E8", "#3A3A5C"))
        infoPanel.grid(row=0, column=1, padx=(16, 0), pady=8, sticky="nsew")

        ctk.CTkLabel(infoPanel, text=productName,
                     font=ctk.CTkFont("Segoe UI", 18, "bold"),
                     wraplength=380,
                     justify="left").pack(anchor="w", padx=20, pady=(20, 12))

        ctk.CTkLabel(infoPanel, text="Description",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=BLUE_PRIMARY).pack(anchor="w", padx=20, pady=(0, 4))
        ctk.CTkLabel(infoPanel, text=description,
                     font=ctk.CTkFont(size=13),
                     wraplength=380,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(infoPanel, text="Recommended Dosage",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=BLUE_PRIMARY).pack(anchor="w", padx=20, pady=(0, 4))
        ctk.CTkLabel(infoPanel, text=dosageProd,
                     font=ctk.CTkFont(size=13),
                     wraplength=380,
                     justify="left").pack(anchor="w", padx=20, pady=(0, 20))

        ctk.CTkLabel(infoPanel, text="Add to Your Prescriptions",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=BLUE_PRIMARY).pack(anchor="w", padx=20, pady=(0, 4))

        ctk.CTkLabel(infoPanel, text="Dosage",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.dosageEntry = ctk.CTkEntry(infoPanel, width=340, height=36,
                                         placeholder_text="e.g. 500mg")
        self.dosageEntry.pack(anchor="w", padx=20, pady=(4, 10))

        ctk.CTkLabel(infoPanel, text="Frequency",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.frequencyEntry = ctk.CTkEntry(infoPanel, width=340, height=36,
                                            placeholder_text="e.g. Twice daily")
        self.frequencyEntry.pack(anchor="w", padx=20, pady=(4, 10))

        ctk.CTkLabel(infoPanel, text="Notes (optional)",
                     font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.notesEntry = ctk.CTkEntry(infoPanel, width=340, height=36,
                                        placeholder_text="e.g. Take after meals")
        self.notesEntry.pack(anchor="w", padx=20, pady=(4, 10))

        self.prescriptionFeedbackLabel = ctk.CTkLabel(infoPanel, text="",
                                                       font=ctk.CTkFont(size=12),
                                                       text_color="#2E7D32",
                                                       wraplength=340)
        self.prescriptionFeedbackLabel.pack(anchor="w", padx=20)

        ctk.CTkButton(infoPanel, text="Add to Prescription",
                      width=220, height=44,
                      fg_color=GREEN_PRIMARY, hover_color=GREEN_HOVER,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=12,
                      command=self.addToPrescription).pack(anchor="w",
                                                            padx=20,
                                                            pady=(8, 20))

    def addToPrescription(self):
        from dbManager import addPrescription

        productId = self.currentProduct[0]
        userId    = self.controller.currentUserId

        if userId is None:
            self.prescriptionFeedbackLabel.configure(
                text_color="#E53935",
                text="You must be logged in to add a prescription.")
            return

        dosagePrs = self.dosageEntry.get().strip()
        frequency = self.frequencyEntry.get().strip()
        notes     = self.notesEntry.get().strip()

        if dosagePrs == "" or frequency == "":
            self.prescriptionFeedbackLabel.configure(
                text_color="#E53935",
                text="Please enter a dosage and frequency before saving.")
            return

        try:
            addPrescription(userId, productId, "", "", "",
                            "", "", dosagePrs, frequency, notes)
            self.prescriptionFeedbackLabel.configure(
                text_color="#2E7D32",
                text="Prescription added successfully.")
            self.dosageEntry.delete(0, "end")
            self.frequencyEntry.delete(0, "end")
            self.notesEntry.delete(0, "end")
        except Exception:
            self.prescriptionFeedbackLabel.configure(
                text_color="#E53935",
                text="Failed to add prescription. Please try again.")
        
        
    def hideProductDetail(self):
        if hasattr(self, "detailFrame"):
            self.detailFrame.destroy()
        self.searchFrame.pack(fill="x", padx=60, pady=(50, 6))
        self.filterFrame.pack(fill="x", padx=60, pady=(4, 8))
        self.scrollFrame.pack(expand=True, fill="both", padx=60, pady=(0, 4))

    def refreshTheme(self):
        label  = "🌙  Dark Mode" if not self.controller.darkMode else "☀  Light Mode"
        colour = "#3A3ACA" if self.controller.darkMode else "#E8B000"
        self.toggleBtn.configure(text=label, fg_color=colour)


## ══════════════════════════════════════════════
#  Prescription Frame
# ══════════════════════════════════════════════
class PrescriptionFrame(ctk.CTkFrame):

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self._buildUI()

    def _buildUI(self):
        titleBar, self.toggleBtn = buildTitleBar(self, self.controller)

        ctk.CTkButton(self, text="← Home", width=90, height=30,
                      fg_color="transparent",
                      hover_color=("#E0E0E0", "#333333"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=12),
                      corner_radius=8,
                      command=lambda: self.controller.showFrame(
                          "HomeFrame")).place(x=10, y=90)

        self.contentArea = ctk.CTkFrame(self, fg_color="transparent")
        self.contentArea.pack(expand=True, fill="both", pady=(40, 0))

    # ── Load and display prescriptions ───────
    def loadPrescriptions(self):
        from dbManager import getPrescriptionsByUserId

        # Destroy whatever is currently in the content area
        self.contentArea.destroy()
        self.contentArea = ctk.CTkFrame(self, fg_color="transparent")
        self.contentArea.pack(expand=True, fill="both", pady=(40, 0))

        ctk.CTkLabel(
            self.contentArea,
            text="Add, view, edit or delete a prescription.",
            font=ctk.CTkFont("Segoe UI", 16),
            text_color=("gray40", "gray70")).pack(pady=(10, 10))

        self.scrollFrame = ctk.CTkScrollableFrame(
            self.contentArea,
            fg_color="transparent",
            scrollbar_button_color=BLUE_PRIMARY,
            scrollbar_button_hover_color=BLUE_DARK)
        self.scrollFrame.pack(expand=True, fill="both",
                              padx=40, pady=(0, 4))

        for col in range(3):
            self.scrollFrame.grid_columnconfigure(
                col, weight=1, uniform="prs")

        self._buildAddCard()

        userId = self.controller.currentUserId
        if userId is None:
            return

        prescriptions = getPrescriptionsByUserId(userId)

        if not prescriptions:
            ctk.CTkLabel(
                self.scrollFrame,
                text="No prescriptions yet. Click Add Prescription "
                     "to get started.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            ).grid(row=0, column=1, columnspan=2, pady=40)
            return

        for index, record in enumerate(prescriptions):
            card = self._makePrescriptionCard(record)
            position = index + 1
            row = position // 3
            col = position % 3
            card.grid(row=row, column=col, padx=10, pady=10,
                      sticky="nsew")

    # ── Add Prescription card ────────────────
    def _buildAddCard(self):
        addCard = ctk.CTkFrame(self.scrollFrame,
                               corner_radius=16,
                               fg_color=(CARD_LIGHT, CARD_DARK),
                               border_width=2,
                               border_color=("#CCCCCC", "#555555"),
                               width=320, height=280)
        addCard.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        addCard.grid_propagate(False)

        circleFrame = ctk.CTkFrame(addCard, width=70, height=70,
                                   corner_radius=35,
                                   fg_color=GREEN_PRIMARY)
        circleFrame.pack(pady=(70, 10))
        circleFrame.pack_propagate(False)

        ctk.CTkLabel(circleFrame, text="＋",
                     font=ctk.CTkFont("Segoe UI", 36, "bold"),
                     text_color="white").place(relx=0.5, rely=0.5,
                                               anchor="center")

        ctk.CTkLabel(addCard, text="Add Prescription",
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color=("black", "white")).pack(pady=(4, 0))

        addCard.bind("<Enter>",
                     lambda e: addCard.configure(
                         border_color=GREEN_PRIMARY))
        addCard.bind("<Leave>",
                     lambda e: addCard.configure(
                         border_color=("#CCCCCC", "#555555")))

        addCard.bind("<Button-1>", lambda e: self.showAddForm())
        for child in addCard.winfo_children():
            child.bind("<Button-1>", lambda e: self.showAddForm())
            for subchild in child.winfo_children():
                subchild.bind("<Button-1>", lambda e: self.showAddForm())

    # ── Show add prescription form ───────────
    def showAddForm(self):
        self.contentArea.destroy()
        self.contentArea = ctk.CTkFrame(self, fg_color="transparent")
        self.contentArea.pack(expand=True, fill="both", pady=(40, 0))

        formScroll = ctk.CTkScrollableFrame(
            self.contentArea, fg_color="transparent",
            scrollbar_button_color=BLUE_PRIMARY,
            scrollbar_button_hover_color=BLUE_DARK)
        formScroll.pack(expand=True, fill="both",
                        padx=120, pady=(0, 4))
        self.formScroll = formScroll

        ctk.CTkLabel(formScroll, text="New Prescription",
                     font=ctk.CTkFont("Segoe UI", 24, "bold")
                     ).pack(pady=(10, 20))

        formCard = ctk.CTkFrame(formScroll, corner_radius=16,
                                fg_color=(CARD_LIGHT, CARD_DARK),
                                border_width=1,
                                border_color=("#D0D8E8", "#3A3A5C"))
        formCard.pack(fill="x", pady=(0, 20))

        def makeField(parent, label, placeholder=""):
            ctk.CTkLabel(parent, text=label,
                         font=ctk.CTkFont("Segoe UI", 13, "bold"),
                         text_color=("black", "white")
                         ).pack(anchor="w", padx=20, pady=(12, 2))
            entry = ctk.CTkEntry(parent, width=400, height=38,
                                 placeholder_text=placeholder,
                                 font=ctk.CTkFont(size=13),
                                 corner_radius=10)
            entry.pack(anchor="w", padx=20, pady=(0, 4))
            return entry

        self.nameEntry        = makeField(formCard, "Full Name",
                                          "e.g. Isaac Hanna")
        self.addressEntry     = makeField(formCard, "Address",
                                          "e.g. 123 Avenue Road")
        self.phoneEntry       = makeField(formCard, "Phone Number",
                                          "e.g. 07123456789")
        self.issueDateEntry   = makeField(formCard, "Issue Date",
                                          "YYYY-MM-DD")
        self.activeUntilEntry = makeField(formCard, "Active Until",
                                          "YYYY-MM-DD")

        from datetime import date
        self.issueDateEntry.insert(0, date.today().strftime("%Y-%m-%d"))

        ctk.CTkLabel(formCard, text="Medicine",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=("black", "white")
                     ).pack(anchor="w", padx=20, pady=(12, 2))

        from dbManager import getAllProducts
        products     = getAllProducts()
        self.productMap = {}
        productNames = []
        for p in products:
            self.productMap[p[1]] = p[0]
            productNames.append(p[1])

        self.productVar = ctk.StringVar(
            value=productNames[0] if productNames else "")
        self.productDropdown = ctk.CTkOptionMenu(
            formCard, variable=self.productVar,
            values=productNames,
            width=400, height=38,
            font=ctk.CTkFont(size=13),
            fg_color=BLUE_PRIMARY,
            button_color=BLUE_DARK,
            corner_radius=10)
        self.productDropdown.pack(anchor="w", padx=20, pady=(0, 4))

        self.addDosageEntry    = makeField(formCard, "Dosage",
                                           "e.g. 500mg")
        self.addFrequencyEntry = makeField(formCard, "Frequency",
                                           "e.g. Twice daily")
        self.addNotesEntry     = makeField(formCard, "Notes (optional)",
                                           "e.g. Take after meals")

        self.addFeedbackLabel = ctk.CTkLabel(
            formCard, text="",
            font=ctk.CTkFont(size=12), wraplength=360)
        self.addFeedbackLabel.pack(anchor="w", padx=20, pady=(8, 4))

        btnRow = ctk.CTkFrame(formCard, fg_color="transparent")
        btnRow.pack(anchor="w", padx=20, pady=(4, 20))

        ctk.CTkButton(btnRow, text="Save Prescription",
                      width=180, height=42,
                      fg_color=GREEN_PRIMARY,
                      hover_color=GREEN_HOVER,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=10,
                      command=self.saveNewPrescription
                      ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btnRow, text="Cancel",
                      width=120, height=42,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=13),
                      corner_radius=10,
                      command=self.hideAddForm
                      ).pack(side="left")

    # ── Hide form and restore card list ──────
    def hideAddForm(self):
        self.loadPrescriptions()

    # ── Build a single prescription card ─────
    def _makePrescriptionCard(self, record):
        from dbManager import getProductById

        (prescriptionId, userId, productId, fullName, address,
         phone, issueDate, activeUntil, dosagePrs,
         frequency, notes) = record

        product     = getProductById(productId)
        productName = product[1] if product else "Unknown Medicine"
        pifNumber   = f"PIF #{prescriptionId:03d}"

        card = ctk.CTkFrame(self.scrollFrame, corner_radius=16,
                            fg_color=(CARD_LIGHT, CARD_DARK),
                            border_width=2,
                            border_color=("#CCCCCC", "#555555"),
                            width=320, height=280)
        card.grid_propagate(False)

        headerFrame = ctk.CTkFrame(card, fg_color="transparent")
        headerFrame.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(headerFrame, text=pifNumber,
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=("black", "white")).pack(anchor="w")
        ctk.CTkLabel(headerFrame,
                     text=f"Issued: {issueDate}",
                     font=ctk.CTkFont(size=10),
                     text_color="gray").pack(anchor="w")

        ctk.CTkLabel(card, text=fullName,
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color=("black", "white")
                     ).pack(anchor="w", padx=12, pady=(6, 0))
        ctk.CTkLabel(card, text=address,
                     font=ctk.CTkFont(size=11),
                     text_color=("gray40", "gray70")
                     ).pack(anchor="w", padx=12)
        ctk.CTkLabel(card, text=phone,
                     font=ctk.CTkFont(size=11),
                     text_color=("gray40", "gray70")
                     ).pack(anchor="w", padx=12)

        ctk.CTkLabel(card,
                     text=f"• {productName}  {dosagePrs}",
                     font=ctk.CTkFont(size=11),
                     text_color=("black", "white")
                     ).pack(anchor="w", padx=12, pady=(8, 0))

        ctk.CTkLabel(card,
                     text=f"Active until {activeUntil}",
                     font=ctk.CTkFont(size=10),
                     text_color="gray"
                     ).pack(anchor="w", padx=12, pady=(8, 0))

        iconRow = ctk.CTkFrame(card, fg_color="transparent")
        iconRow.pack(anchor="e", padx=12, pady=(4, 10))

        ctk.CTkButton(iconRow, text="👁", width=32, height=32,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      font=ctk.CTkFont(size=14),
                      corner_radius=8,
                      command=lambda pid=prescriptionId:
                          self.showEditForm(pid)
                      ).pack(side="left", padx=2)

        ctk.CTkButton(iconRow, text="✏️", width=32, height=32,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      font=ctk.CTkFont(size=14),
                      corner_radius=8,
                      command=lambda pid=prescriptionId:
                          self.showEditForm(pid)
                      ).pack(side="left", padx=2)

        ctk.CTkButton(iconRow, text="🗑", width=32, height=32,
                      fg_color=("#FFCDD2", "#5C2828"),
                      hover_color=("#EF9A9A", "#7C3838"),
                      font=ctk.CTkFont(size=14),
                      corner_radius=8,
                      command=lambda pid=prescriptionId:
                          self.confirmDelete(pid)
                      ).pack(side="left", padx=2)

        card.bind("<Enter>",
                  lambda e: card.configure(
                      border_color=BLUE_PRIMARY))
        card.bind("<Leave>",
                  lambda e: card.configure(
                      border_color=("#CCCCCC", "#555555")))

        return card

    # ── Save prescription to database ────────
    def saveNewPrescription(self):
        from dbManager import addPrescription

        userId = self.controller.currentUserId
        if userId is None:
            self.addFeedbackLabel.configure(
                text_color="#E53935",
                text="You must be logged in to add a prescription.")
            return

        fullName    = self.nameEntry.get().strip()
        address     = self.addressEntry.get().strip()
        phone       = self.phoneEntry.get().strip()
        issueDate   = self.issueDateEntry.get().strip()
        activeUntil = self.activeUntilEntry.get().strip()
        dosagePrs   = self.addDosageEntry.get().strip()
        frequency   = self.addFrequencyEntry.get().strip()
        notes       = self.addNotesEntry.get().strip()

        if (fullName == "" or address == "" or phone == ""
                or issueDate == "" or activeUntil == ""
                or dosagePrs == "" or frequency == ""):
            self.addFeedbackLabel.configure(
                text_color="#E53935",
                text="Please fill in all required fields before saving.")
            return
        
        dateError = self.validateDates(issueDate, activeUntil)
        if dateError:
            self.addFeedbackLabel.configure(
                text_color="#E53935", text=dateError)
            return
        
        selectedProduct = self.productVar.get()
        productId = self.productMap.get(selectedProduct)

        try:
            addPrescription(userId, productId, fullName, address,
                            phone, issueDate, activeUntil,
                            dosagePrs, frequency, notes)
            self.addFeedbackLabel.configure(
                text_color="#2E7D32",
                text="Prescription added successfully.")
        except Exception:
            self.addFeedbackLabel.configure(
                text_color="#E53935",
                text="Failed to add prescription. Please try again.")

# ── Validate date fields ─────────────────
    def validateDates(self, issueDate, activeUntil):
        import re
        datePattern = r"^\d{4}-\d{2}-\d{2}$"

        if not re.match(datePattern, issueDate):
            return "Issue date must be in YYYY-MM-DD format."
        if not re.match(datePattern, activeUntil):
            return "Active until date must be in YYYY-MM-DD format."
        if activeUntil < issueDate:
            return "Active until date cannot be earlier than issue date."
        return None

    # ── Show edit prescription form ──────────
    def showEditForm(self, prescriptionId):
        from dbManager import getPrescriptionById, getAllProducts

        record = getPrescriptionById(prescriptionId)
        if record is None:
            return

        (pId, uId, productId, fullName, address, phone,
         issueDate, activeUntil, dosagePrs, frequency, notes) = record

        self.editingId = prescriptionId

        self.contentArea.destroy()
        self.contentArea = ctk.CTkFrame(self, fg_color="transparent")
        self.contentArea.pack(expand=True, fill="both", pady=(40, 0))

        formScroll = ctk.CTkScrollableFrame(
            self.contentArea, fg_color="transparent",
            scrollbar_button_color=BLUE_PRIMARY,
            scrollbar_button_hover_color=BLUE_DARK)
        formScroll.pack(expand=True, fill="both",
                        padx=120, pady=(0, 4))

        ctk.CTkLabel(formScroll,
                     text=f"Edit Prescription — PIF #{prescriptionId:03d}",
                     font=ctk.CTkFont("Segoe UI", 24, "bold")
                     ).pack(pady=(10, 20))

        formCard = ctk.CTkFrame(formScroll, corner_radius=16,
                                fg_color=(CARD_LIGHT, CARD_DARK),
                                border_width=1,
                                border_color=("#D0D8E8", "#3A3A5C"))
        formCard.pack(fill="x", pady=(0, 20))

        def makeField(parent, label, value=""):
            ctk.CTkLabel(parent, text=label,
                         font=ctk.CTkFont("Segoe UI", 13, "bold"),
                         text_color=("black", "white")
                         ).pack(anchor="w", padx=20, pady=(12, 2))
            entry = ctk.CTkEntry(parent, width=400, height=38,
                                 font=ctk.CTkFont(size=13),
                                 corner_radius=10)
            entry.pack(anchor="w", padx=20, pady=(0, 4))
            entry.insert(0, value)
            return entry

        self.editNameEntry       = makeField(formCard, "Full Name",
                                             fullName)
        self.editAddressEntry    = makeField(formCard, "Address",
                                             address)
        self.editPhoneEntry      = makeField(formCard, "Phone Number",
                                             phone)
        self.editIssueDateEntry  = makeField(formCard, "Issue Date",
                                             issueDate)
        self.editActiveUntilEntry = makeField(formCard, "Active Until",
                                              activeUntil)

        # ── Product dropdown ──
        ctk.CTkLabel(formCard, text="Medicine",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=("black", "white")
                     ).pack(anchor="w", padx=20, pady=(12, 2))

        products     = getAllProducts()
        self.editProductMap = {}
        productNames = []
        currentProductName = ""
        for p in products:
            self.editProductMap[p[1]] = p[0]
            productNames.append(p[1])
            if p[0] == productId:
                currentProductName = p[1]

        self.editProductVar = ctk.StringVar(value=currentProductName)
        editDropdown = ctk.CTkOptionMenu(
            formCard, variable=self.editProductVar,
            values=productNames,
            width=400, height=38,
            font=ctk.CTkFont(size=13),
            fg_color=BLUE_PRIMARY,
            button_color=BLUE_DARK,
            corner_radius=10)
        editDropdown.pack(anchor="w", padx=20, pady=(0, 4))
        editDropdown.set(currentProductName)

        self.editDosageEntry    = makeField(formCard, "Dosage",
                                            dosagePrs)
        self.editFrequencyEntry = makeField(formCard, "Frequency",
                                            frequency)
        self.editNotesEntry     = makeField(formCard, "Notes (optional)",
                                            notes if notes else "")

        self.editFeedbackLabel = ctk.CTkLabel(
            formCard, text="",
            font=ctk.CTkFont(size=12), wraplength=360)
        self.editFeedbackLabel.pack(anchor="w", padx=20, pady=(8, 4))

        btnRow = ctk.CTkFrame(formCard, fg_color="transparent")
        btnRow.pack(anchor="w", padx=20, pady=(4, 20))

        ctk.CTkButton(btnRow, text="Save Changes",
                      width=180, height=42,
                      fg_color=GREEN_PRIMARY,
                      hover_color=GREEN_HOVER,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=10,
                      command=self.saveEditPrescription
                      ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btnRow, text="Cancel",
                      width=120, height=42,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=13),
                      corner_radius=10,
                      command=self.loadPrescriptions
                      ).pack(side="left")

    # ── Save edited prescription ─────────────
    def saveEditPrescription(self):
        from dbManager import updatePrescription

        fullName    = self.editNameEntry.get().strip()
        address     = self.editAddressEntry.get().strip()
        phone       = self.editPhoneEntry.get().strip()
        issueDate   = self.editIssueDateEntry.get().strip()
        activeUntil = self.editActiveUntilEntry.get().strip()
        dosagePrs   = self.editDosageEntry.get().strip()
        frequency   = self.editFrequencyEntry.get().strip()
        notes       = self.editNotesEntry.get().strip()

        if (fullName == "" or address == "" or phone == ""
                or issueDate == "" or activeUntil == ""
                or dosagePrs == "" or frequency == ""):
            self.editFeedbackLabel.configure(
                text_color="#E53935",
                text="Please fill in all required fields before saving.")
            return

        dateError = self.validateDates(issueDate, activeUntil)
        if dateError:
            self.editFeedbackLabel.configure(
                text_color="#E53935", text=dateError)
            return

        try:
            updatePrescription(self.editingId, fullName, address,
                               phone, issueDate, activeUntil,
                               dosagePrs, frequency, notes)
            self.editFeedbackLabel.configure(
                text_color="#2E7D32",
                text="Prescription updated successfully.")
        except Exception:
            self.editFeedbackLabel.configure(
                text_color="#E53935",
                text="Failed to update prescription. Please try again.")

    # ── Confirm and delete prescription ──────
    def confirmDelete(self, prescriptionId):
        pifNumber = f"PIF #{prescriptionId:03d}"

        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Deletion")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()

        ctk.CTkLabel(dialog,
                     text=f"Delete {pifNumber}?",
                     font=ctk.CTkFont("Segoe UI", 18, "bold")
                     ).pack(pady=(30, 10))

        ctk.CTkLabel(dialog,
                     text="This action cannot be undone.",
                     font=ctk.CTkFont(size=12),
                     text_color="gray").pack(pady=(0, 20))

        btnRow = ctk.CTkFrame(dialog, fg_color="transparent")
        btnRow.pack()

        def executeDelete():
            from dbManager import deletePrescription
            deletePrescription(prescriptionId)
            dialog.destroy()
            self.loadPrescriptions()

        ctk.CTkButton(btnRow, text="Delete",
                      width=120, height=38,
                      fg_color="#E53935",
                      hover_color="#C62828",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      corner_radius=10,
                      command=executeDelete
                      ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btnRow, text="Cancel",
                      width=120, height=38,
                      fg_color=("#E0E0E0", "#3A3A3A"),
                      hover_color=("#C8C8C8", "#4A4A4A"),
                      text_color=("black", "white"),
                      font=ctk.CTkFont(size=13),
                      corner_radius=10,
                      command=dialog.destroy
                      ).pack(side="left")




    def refreshTheme(self):
        label  = "🌙  Dark Mode" if not self.controller.darkMode \
                 else "☀  Light Mode"
        colour = "#3A3ACA" if self.controller.darkMode else "#E8B000"
        self.toggleBtn.configure(text=label, fg_color=colour)

# ══════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════
if __name__ == "__main__":
    app = PharosApp()
    app.mainloop()