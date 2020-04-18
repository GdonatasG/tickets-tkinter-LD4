def clearWindow(window):
    "Metodas skirtas pasalinti visus lange esancius elementus (widgets)"
    for widget in window.winfo_children():
        widget.destroy()
    window.pack_forget()
    window.grid_forget()
