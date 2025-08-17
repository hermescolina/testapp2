from googletrans import Translator


def translate_text(text: str, target_language: str) -> str:
    """Translate text to a target language using googletrans.

    Args:
        text: The text to translate.
        target_language: Language code to translate the text to.

    Returns:
        The translated text, or the original text if translation fails.
    """
    translator = Translator()
    try:
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception:
        return text
