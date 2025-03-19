from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty
import asyncio
import websockets
import json
import threading
from functools import partial

class ChatLayout(BoxLayout):
    pass

class ChatApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.websocket = None
        self.client_name = "User"
        self._connection_thread = None
        
    def build(self):
        # Start WebSocket connection in a separate thread
        self._connection_thread = threading.Thread(target=self.setup_websocket, daemon=True)
        self._connection_thread.start()
        return ChatLayout()

    def setup_websocket(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def connect():
            try:
                self.websocket = await websockets.connect('ws://localhost:8765')
                await self.receive_messages()
            except Exception as e:
                print(f"Connection error: {e}")

        loop.run_until_complete(connect())

    async def receive_messages(self):
        try:
            async for message in self.websocket:
                # Schedule the UI update in the main thread
                Clock.schedule_once(partial(self.add_message, message))
        except websockets.ConnectionClosed:
            print("Connection to server closed")
        except Exception as e:
            print(f"Error receiving messages: {e}")

    def add_message(self, message, *args):
        try:
            chat_history = self.root.ids.chat_history
            
            # Create message label with proper styling
            label = Label(
                text=message,
                size_hint_y=None,
                height=40,
                text_size=(chat_history.width * 0.9, None),
                halign='left',
                valign='middle'
            )
            
            chat_history.add_widget(label)
        except Exception as e:
            print(f"Error adding message: {e}")

    def send_message(self):
        message_input = self.root.ids.message_input
        if message_input.text.strip():
            message = f"{self.client_name}: {message_input.text}"
            
            def send_in_thread():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                async def send():
                    if self.websocket:
                        try:
                            await self.websocket.send(message)
                        except Exception as e:
                            print(f"Error sending message: {e}")

                loop.run_until_complete(send())
                loop.close()

            threading.Thread(target=send_in_thread, daemon=True).start()
            message_input.text = ""  # Clear input field

    def on_stop(self):
        async def cleanup():
            if self.websocket:
                await self.websocket.close()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(cleanup())
        loop.close()

if __name__ == '__main__':
    Window.size = (400, 600)  # Set a reasonable default size for mobile
    ChatApp().run() 