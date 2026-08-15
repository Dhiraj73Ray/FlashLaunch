import keyboard

print("Press Fn+Space...")

keyboard.add_hotkey("Fn+space", lambda: print("HOTKEY WORKED"))

keyboard.wait()