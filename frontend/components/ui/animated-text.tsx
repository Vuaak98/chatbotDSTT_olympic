"use client";

import { animate } from "framer-motion";
import { useEffect, useState, useRef } from "react";

// Define options for delimiter and animation speed
interface AnimatedTextOptions {
  delimiter?: string;       // "" for chars, " " for words
  charSpeed?: number;       // characters per second
  wordSpeed?: number;       // words per second
  onFinish?: () => void;    // optional callback when animation completes
  prevText?: string;       // previous text to animate from
}

export function useAnimatedText(
  text: string,
  options: AnimatedTextOptions = {}
) {
  const {
    delimiter = "",
    charSpeed = 60,
    wordSpeed = 20,
    onFinish,
    prevText,
  } = options;
  const [cursor, setCursor] = useState(0);
  const [startingCursor, setStartingCursor] = useState(0);
  const [internalPrevText, setInternalPrevText] = useState(text);
  // Skip animation on initial mount
  const isFirstRender = useRef(true);

  // Move appended text detection into useEffect for correct state sync
  useEffect(() => {
    const compareText = prevText !== undefined ? prevText : internalPrevText;
    if (compareText !== text) {
      if (prevText === undefined) setInternalPrevText(text);
      setStartingCursor(text.startsWith(compareText) ? cursor : 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, prevText]);

  useEffect(() => {
    const parts = text.split(delimiter);
    // On initial render, show full text without animation
    if (isFirstRender.current) {
      setCursor(parts.length);
      isFirstRender.current = false;
      return;
    }
    // Compute how many new parts to animate
    const newCount = parts.length - startingCursor;
    // Choose speed based on delimiter
    const speed = delimiter === "" ? charSpeed : wordSpeed;
    // Duration = parts to animate / rate
    const duration = newCount / speed;

    const controls = animate(startingCursor, parts.length, {
      duration,
      ease: "linear",
      onUpdate(latest) {
        setCursor(Math.floor(latest));
      },
      onComplete() {
        // Notify when animation finishes
        onFinish?.();
      }
    });

    return () => controls.stop();
  }, [startingCursor, text, delimiter, charSpeed, wordSpeed]);

  return text.split(delimiter).slice(0, cursor).join(delimiter);
}