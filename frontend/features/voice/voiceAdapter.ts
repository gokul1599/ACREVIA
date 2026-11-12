// ACREVIA Vernacular Voice Interaction Adapter (Telugu, Hindi, Indian English)
export type SpeechLocale = "te-IN" | "hi-IN" | "en-IN";

interface SpeechRecognitionEvent {
  results: {
    [index: number]: {
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognitionInstance {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: { error: string }) => void;
  onend: () => void;
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SpeechRecognitionInstance;
    webkitSpeechRecognition?: new () => SpeechRecognitionInstance;
  }
}

export class VoiceAdapter {
  static isSpeechRecognitionSupported(): boolean {
    if (typeof window === "undefined") return false;
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  static isSpeechSynthesisSupported(): boolean {
    if (typeof window === "undefined") return false;
    return "speechSynthesis" in window;
  }

  static getLocaleCode(lang: "te" | "en" | "hi"): SpeechLocale {
    switch (lang) {
      case "te":
        return "te-IN";
      case "hi":
        return "hi-IN";
      case "en":
      default:
        return "en-IN";
    }
  }

  static createRecognizer(
    lang: "te" | "en" | "hi",
    onResult: (transcript: string) => void,
    onError: (err: string) => void,
    onEnd: () => void
  ): { start: () => void; stop: () => void } | null {
    if (!this.isSpeechRecognitionSupported()) {
      return null;
    }

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) return null;

    try {
      const recognition = new SpeechRec();
      recognition.lang = this.getLocaleCode(lang);
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        if (event.results && event.results[0] && event.results[0][0]) {
          const text = event.results[0][0].transcript;
          onResult(text);
        }
      };

      recognition.onerror = (event: { error: string }) => {
        onError(event.error || "Speech recognition error");
      };

      recognition.onend = () => {
        onEnd();
      };

      return {
        start: () => recognition.start(),
        stop: () => recognition.stop(),
      };
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Recognizer initialization failed";
      onError(msg);
      return null;
    }
  }

  static speakText(text: string, lang: "te" | "en" | "hi"): boolean {
    if (!this.isSpeechSynthesisSupported()) return false;

    window.speechSynthesis.cancel(); // Stop any pending utterances
    const cleanText = text.replace(/[*#_`]/g, ""); // strip markdown tokens
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = this.getLocaleCode(lang);
    utterance.rate = 0.95; // Slightly slower, clear cadence for agricultural advice

    window.speechSynthesis.speak(utterance);
    return true;
  }

  static stopSpeaking() {
    if (this.isSpeechSynthesisSupported()) {
      window.speechSynthesis.cancel();
    }
  }
}
