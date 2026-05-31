import flet as ft
import socket
import threading
import os

class ServerApp:
    def __init__(self):
        self.server = None
        self.running = False
        self.clients = []
    
    def start_server(self, page, port=8004):
        self.running = True
        
        def run():
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(("0.0.0.0", port))
            self.server.listen(5)
            
            page.add(ft.Text(f"✅ خادم يعمل على المنفذ {port}", color=ft.colors.GREEN))
            page.update()
            
            while self.running:
                try:
                    self.server.settimeout(1)
                    client, addr = self.server.accept()
                    page.add(ft.Text(f"🔗 اتصال من: {addr}", color=ft.colors.BLUE))
                    page.update()
                    threading.Thread(target=self.handle_client, args=(client, page), daemon=True).start()
                except socket.timeout:
                    continue
                except:
                    break
        
        threading.Thread(target=run, daemon=True).start()
    
    def handle_client(self, client, page):
        while self.running:
            try:
                command = client.recv(4096).decode()
                if not command or command.lower() == 'exit':
                    break
                
                output = os.popen(command).read()
                if not output:
                    output = "✅ تم التنفيذ"
                client.send(output.encode())
                
                # عرض الأمر في الواجهة
                page.add(ft.Text(f"📥 أمر: {command}", color=ft.colors.YELLOW))
                page.update()
                
            except:
                break
        client.close()
    
    def stop_server(self):
        self.running = False
        if self.server:
            self.server.close()

def main(page: ft.Page):
    page.title = "Socket Server Controller"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.scroll = ft.ScrollMode.AUTO
    
    app = ServerApp()
    
    # عناصر الواجهة
    title = ft.Text("🖥️ التحكم في خادم Socket", size=24, weight=ft.FontWeight.BOLD)
    port_field = ft.TextField(label="المنفذ", value="8004", width=200)
    
    status_text = ft.Text("⚪ الخادم متوقف", color=ft.colors.RED)
    log_area = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=300)
    
    def start(e):
        port = int(port_field.value)
        app.start_server(page, port)
        status_text.value = f"🟢 الخادم يعمل على المنفذ {port}"
        status_text.color = ft.colors.GREEN
        page.update()
    
    def stop(e):
        app.stop_server()
        status_text.value = "🔴 الخادم متوقف"
        status_text.color = ft.colors.RED
        page.update()
    
    start_btn = ft.ElevatedButton("▶ بدء الخادم", on_click=start, bgcolor=ft.colors.GREEN, color=ft.colors.WHITE)
    stop_btn = ft.ElevatedButton("⏹ إيقاف الخادم", on_click=stop, bgcolor=ft.colors.RED, color=ft.colors.WHITE)
    
    page.add(
        title,
        ft.Row([port_field], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([start_btn, stop_btn], alignment=ft.MainAxisAlignment.CENTER),
        status_text,
        ft.Divider(),
        ft.Text("📋 سجل الأحداث:", weight=ft.FontWeight.BOLD),
        ft.Container(log_area, border=ft.border.all(1, ft.colors.GREY), padding=10, height=300),
    )

ft.app(target=main)
