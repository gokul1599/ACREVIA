import test from "node:test";
import assert from "node:assert";
import { VoiceAdapter } from "../features/voice/voiceAdapter.ts";

test("VoiceAdapter - language code resolution", () => {
  assert.strictEqual(VoiceAdapter.getLocaleCode("te"), "te-IN");
  assert.strictEqual(VoiceAdapter.getLocaleCode("hi"), "hi-IN");
  assert.strictEqual(VoiceAdapter.getLocaleCode("en"), "en-IN");
});

test("VoiceAdapter - safely handles environments without window", () => {
  // In pure Node.js environment without Web Speech API
  assert.strictEqual(VoiceAdapter.isSpeechRecognitionSupported(), false);
  assert.strictEqual(VoiceAdapter.isSpeechSynthesisSupported(), false);

  const recognizer = VoiceAdapter.createRecognizer(
    "te",
    () => {},
    () => {},
    () => {}
  );
  assert.strictEqual(recognizer, null);
});
