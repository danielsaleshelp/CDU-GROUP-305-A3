#Group name:[Cas group 305]
#Group Members:
#[Reece Colgan] - S377586
#[Hayden Powell] - S376682
#[Daniel Sales] - S322244
#[Luke Few] - S348831
# Group 305 - Language translation app

import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from googletrans import Translator

# Base class for translation service
class TranslatorService:
    def __init__(self):
        self.translator = Translator()  # Encapsulation: Keeps the translator object private
                                        # Data Hiding: The translator object is not accessible outside this class

    # Method to perform translation with error handling
    def translate(self, text, src_lang, dest_lang):
        try:
            translated = self.translator.translate(text, src=src_lang, dest=dest_lang)
            return translated.text
        except Exception as e:
            return "Error: " + str(e)  # Error Handling: Catches any exception and returns an error message

# Class for providing language options
class LanguagePicker:
    def __init__(self):
        self._languages = [  # Using an underscore to show it's intended as a "private" attribute
            'English', 'Spanish', 'French', 
            'German', 'Chinese (Simplified)', 
            'Russian', 'Japanese', 
            'Portuguese', 'Hindi', 'Arabic'
        ]

    @property  # Decorator 1: Provides a read-only property for accessing the language list.
    def languages(self):
        return self._languages  # Encapsulation: This makes the language list read-only

# Combined class
class EnhancedTranslator(TranslatorService, LanguagePicker):  # Multiple Inheritance: Combines functionalities from both parent classes
    def __init__(self):
        TranslatorService.__init__(self)  # Initialize the translator service
        LanguagePicker.__init__(self)  # Initialize language options

    @staticmethod  # Decorator 2: This static method is independent of class/instance state.
    def is_text_empty(text):
        return not bool(text.strip())  # Checks if the provided text is empty or contains only spaces

    # Overriding the translate method to add logging
    def translate(self, text, src_lang, dest_lang):
        result = super().translate(text, src_lang, dest_lang)  # Call the base class method to perform translation
        print(f"Translated '{text}' from {src_lang} to {dest_lang}: {result}")  # Adds logging functionality
        return result

# Main application class
class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translation App")  # Set window title
        self.root.geometry("700x500")  # Set window size
        
        # Load the image 
        self.image = PhotoImage(file="cdu.png")  # Keep a reference
        
        # Create a label to display the image
        image_label = tk.Label(self.root, image=self.image)
        image_label.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=10)

        # Add a header label with larger, bold font
        header = tk.Label(self.root, text="CDU-Group 305 \n Language Translation App", font=("Helvetica", 16, "bold"))  
        header.pack(pady=20)

        self.translator = EnhancedTranslator()  # Use the combined translator class
        self.create_widgets()  # Build the UI

    def create_widgets(self):
        # Frame for text input
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=20)

        # Label for input field
        tk.Label(input_frame, text="Enter text:").pack(side=tk.LEFT)

        # Input box for text
        self.input_text = tk.Entry(input_frame, width=30)
        self.input_text.pack(side=tk.LEFT)  

        # Language selection frame
        lang_frame = tk.Frame(self.root)  
        lang_frame.pack(pady=20)

        self.lang_from = tk.StringVar(value='English')   # Source language   
        self.lang_to = tk.StringVar(value='Spanish')    # Destination language   

        # Language dropdowns
        tk.Label(lang_frame, text="From:").pack(side=tk.LEFT)
        self.from_menu = tk.OptionMenu(lang_frame, self.lang_from, *self.translator.languages)  # Accessing language list using the @property decorator
        self.from_menu.pack(side=tk.LEFT)
        

        tk.Label(lang_frame, text="To:").pack(side=tk.LEFT)
        self.to_menu = tk.OptionMenu(lang_frame, self.lang_to, *self.translator.languages)    
        self.to_menu.pack(side=tk.LEFT)

        # Translate button
        tk.Button(self.root, text="Translate", command=self.perform_translation,).pack(pady=20)  

        # Label for output translation
        self.output_label = tk.Label(self.root, text="", fg="blue")  
        self.output_label.pack(pady=(10, 20))

    def perform_translation(self):
        # Get the input text and languages for translation
        text = self.input_text.get().strip()
        src_lang = self.lang_from.get()
        dest_lang = self.lang_to.get()

        # Use the static method to check if the input text is empty
        if EnhancedTranslator.is_text_empty(text):  # Polymorphism: A static method defined in the EnhancedTranslator class
            messagebox.showwarning("Input Error", "Please enter text to translate.")
            return

        # Call the translate method from EnhancedTranslator
        result = self.translator.translate(text, src_lang, dest_lang)  # Polymorphism: translate() behaves differently depending on the class
        self.output_label.config(text=result)  # Update output label with translation result

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)  # Create the app instance
    root.mainloop()  # Run the application