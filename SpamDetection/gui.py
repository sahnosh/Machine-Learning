"""Local desktop UI; messages never leave this computer."""
import tkinter as tk
from tkinter import ttk, messagebox
from spam_detector import load_model, predict

def main():
    window=tk.Tk()
    window.title('Spam Detection | English SMS')
    window.geometry('720x480')
    window.minsize(580,400)
    window.configure(bg='#f1f5f9')
    frame=ttk.Frame(window,padding=28)
    frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='SMS Spam Detector',font=('Segoe UI',22,'bold')).pack(anchor='w')
    ttk.Label(frame,text='Enter an English message. Processing stays on your computer.',font=('Segoe UI',10)).pack(anchor='w',pady=(8,20))
    editor=tk.Text(frame,height=8,wrap='word',font=('Segoe UI',12),relief='solid',bd=1)
    editor.pack(fill='both',expand=True)
    result=tk.StringVar(value='Ready to classify')
    score=tk.StringVar(value='Trained on English SMS. Dari/Persian messages are not supported.')
    try: model=load_model()
    except Exception as exc:
        messagebox.showerror('Model unavailable',str(exc))
        window.destroy()
        return
    def classify():
        try:
            prediction=predict(editor.get('1.0','end'),model)
            result.set('SPAM - unwanted message' if prediction['label']=='spam' else 'HAM - normal message')
            score.set(f"Spam score: {prediction['spam_score']:.1%} (not a calibrated probability)")
        except ValueError as exc:
            result.set('Message cannot be classified')
            score.set(str(exc))
    ttk.Button(frame,text='Check message',command=classify).pack(anchor='w',pady=16)
    ttk.Label(frame,textvariable=result,font=('Segoe UI',15,'bold')).pack(anchor='w')
    ttk.Label(frame,textvariable=score,wraplength=620).pack(anchor='w',pady=8)
    window.mainloop()

if __name__=='__main__': main()
