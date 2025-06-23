#!/usr/bin/env python3
"""
Main entry point for Jeeves AI Assistant.
Handles global hotkey activation and application lifecycle.
"""
import sys
import signal
import logging
import threading
import time
from pathlib import Path
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
from src.gui.app import JeevesApp
from src.utils.dialogs import show_error
# Configure logging
# search for: loglevel, logginglevel, info, debug, warning, error, critical
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jeeves.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global hotkey detection and handling."""
    
    def __init__(self, app: JeevesApp):
        self.app = app
        self.listener = None
        self.hotkey_pressed = False
        self.pressed_keys = set()
    
    def start(self):
        """Start listening for global hotkeys."""
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.listener.start()
            logger.info("Global hotkey listener started (Alt+Space)")
            logger.info("Press Alt+Space to show/hide the application")
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            raise
    
    def stop(self):
        """Stop listening for global hotkeys."""
        if self.listener:
            self.listener.stop()
            self.listener = None
            logger.info("Global hotkey listener stopped")
    
    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            # Add key to pressed keys set
            self.pressed_keys.add(key)
            
            # Check for Alt+Space combination
            alt_pressed = Key.alt in self.pressed_keys or Key.alt_l in self.pressed_keys
            space_pressed = Key.space in self.pressed_keys
            
            if alt_pressed and space_pressed and not self.hotkey_pressed:
                self.hotkey_pressed = True
                logger.info("Alt+Space detected - activating hotkey")
                self._handle_hotkey_activation()
                
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events."""
        try:
            # Remove key from pressed keys set
            self.pressed_keys.discard(key)
            
            # Reset hotkey state when either Alt or Space is released
            if key in [Key.alt, Key.alt_l, Key.space]:
                self.hotkey_pressed = False
                
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")
    
    def _handle_hotkey_activation(self):
        """Handle hotkey activation."""
        try:
            if self.app.is_visible():
                self.app.hide_window()
                logger.info("Application hidden via hotkey")
            else:
                self.app.show_window()
                logger.info("Application shown via hotkey")
        except Exception as e:
            logger.error(f"Error handling hotkey activation: {e}")


class ApplicationManager:
    """Manages the application lifecycle and coordination."""
    
    def __init__(self):
        self.app = None
        self.hotkey_manager = None
        self.running = False
        self.shutdown_event = threading.Event()
    
    def start(self):
        """Start the application."""
        try:
            logger.info("Starting Jeeves AI Assistant...")
            
            # Create and start the GUI application
            self.app = JeevesApp()
            
            # Start the application hidden
            self.app.hide_window()
            
            # Create and start hotkey manager
            self.hotkey_manager = HotkeyManager(self.app)
            self.hotkey_manager.start()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self.running = True
            logger.info("Application started successfully (hidden, press Alt+Space to show)")
            
            # Run the application
            self.app.run()
            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            show_error("Startup Error", f"Failed to start Jeeves: {e}")
            raise
        finally:
            self.shutdown()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            self.shutdown_event.set()
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def shutdown(self):
        """Shutdown the application gracefully."""
        if not self.running:
            return
        
        logger.info("Shutting down application...")
        self.running = False
        
        try:
            # Stop hotkey manager
            if self.hotkey_manager:
                self.hotkey_manager.stop()
            
            # Close application
            if self.app:
                self.app.shutdown()
            
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """Main entry point."""
    try:
        # Ensure we're in the correct directory
        script_dir = Path(__file__).parent
        if script_dir.exists():
            import os
            os.chdir(script_dir)
        
        # Create and start application manager
        app_manager = ApplicationManager()
        app_manager.start()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application failed: {e}")
        show_error("Fatal Error", f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
