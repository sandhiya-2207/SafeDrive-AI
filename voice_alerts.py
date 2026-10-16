import pyttsx3


def speak_alert(message):
    """
    Speak a safety message using the computer's text-to-speech engine.

    This is an optional demonstration feature.
    """

    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.say(str(message))
        engine.runAndWait()
        engine.stop()

        return True, "Voice alert completed."

    except Exception as error:
        return False, f"Voice alert unavailable: {error}"