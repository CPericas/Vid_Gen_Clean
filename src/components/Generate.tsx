import { useEffect, useState, useRef } from "react";
import { Container, Row, Col, Spinner, Alert, Button } from "react-bootstrap";
import { motion } from "framer-motion";
import { usePrompt } from "../context/PromptContext";
import { useAvatar } from "../context/AvatarContext";
import { useSceneSettings } from "../context/SceneSettingsContext";

export default function Generate() {
  const { prompt } = usePrompt();
  const { avatar } = useAvatar();
  const { selectedMusic } = useSceneSettings();

  const [voiceoverSrc, setVoiceoverSrc] = useState<string | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingStep, setLoadingStep] = useState<"tts" | "video" | null>(null);

  const voiceRef = useRef<HTMLAudioElement | null>(null);
  const musicRef = useRef<HTMLAudioElement | null>(null);

  const fadeVolume = (
    audio: HTMLAudioElement,
    from: number,
    to: number,
    duration: number = 500
  ) => {
    const steps = 10;
    const stepTime = duration / steps;
    const stepSize = (to - from) / steps;
    let current = from;
    let count = 0;

    const interval = setInterval(() => {
      current += stepSize;
      audio.volume = Math.max(0, Math.min(1, current));
      count++;
      if (count >= steps) clearInterval(interval);
    }, stepTime);
  };

  const resetState = () => {
    setError(null);
    setLoadingStep(null);
    setVoiceoverSrc(null);
    setVideoSrc(null);
  };

  // Generate TTS voiceover 
  useEffect(() => {
    if (!prompt) return;

    resetState();
    setLoadingStep("tts");

    const generateTTSAudio = async () => {
      try {
        const response = await fetch("http://localhost:5001/generate-audio", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: prompt }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setVoiceoverSrc("http://localhost:5001/audio/output.wav");
          setLoadingStep("video");

          if (musicRef.current) {
            fadeVolume(musicRef.current, 1, 0.2, 500);
          }
        } else {
          throw new Error(data.error || "TTS generation failed");
        }
      } catch (err: any) {
        setError(`Audio generation error: ${err.message || err}`);
        setLoadingStep(null);
      }
    };

    generateTTSAudio();
  }, [prompt]);

  // Generate lip synced video
  useEffect(() => {
    if (!voiceoverSrc || !avatar) return;

    const generateVideo = async () => {
      try {
        console.log("Sending avatar to backend:", avatar);
        const response = await fetch("http://localhost:5001/generate-video", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            avatar: avatar,   // ✅ use selected avatar from context
            mode: "full",
            audioPath: "output.wav",
          }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
          setVideoSrc("http://localhost:5001/video/output.mp4");
          setLoadingStep(null);
        } else {
          throw new Error(data.error || "Video generation failed");
        }
      } catch (err: any) {
        setError(`Video generation error: ${err.message || err}`);
        setLoadingStep(null);
      }
    };

    generateVideo();
  }, [voiceoverSrc, avatar]);

  const handleRetry = () => {
    resetState();
    window.location.reload();
  };

  return (
    <Container className="py-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Row className="justify-content-center py-5">
          <Col md={8} className="text-center">
            {loadingStep && (
              <>
                <Spinner animation="border" variant="primary" />
                <p className="mt-3">
                  {loadingStep === "tts"
                    ? "Generating voiceover audio..."
                    : "Generating video..."}
                </p>
              </>
            )}

            {error && (
              <Alert variant="danger" className="my-3">
                {error}
                <div className="mt-3">
                  <Button onClick={handleRetry}>Try Again</Button>
                </div>
              </Alert>
            )}

            {videoSrc && !error && (
              <>
                <video
                  src={videoSrc}
                  controls
                  autoPlay
                  loop
                  style={{ width: "100%", borderRadius: "10px" }}
                />
                <div className="mt-3">
                  <Button
                    as="a"
                    variant="success"
                    href={videoSrc}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download Video
                  </Button>
                </div>
              </>
            )}
          </Col>
        </Row>

        {!videoSrc && voiceoverSrc && !error && (
          <Row className="justify-content-center py-3">
            <Col className="text-center" md={6}>
              <audio
                ref={voiceRef}
                controls
                preload="auto"
                style={{ width: "100%" }}
                onEnded={() => {
                  if (musicRef.current) {
                    fadeVolume(musicRef.current, 0.2, 1, 500);
                  }
                }}
              >
                <source src={voiceoverSrc} type="audio/wav" />
                Your browser does not support the audio element.
              </audio>
            </Col>
          </Row>
        )}

        <Row className="justify-content-center py-5">
          <Col className="text-center" md={6}>
            {selectedMusic ? (
              <audio
                ref={musicRef}
                controls
                preload="auto"
                style={{ width: "100%" }}
              >
                <source src={selectedMusic} type="audio/mpeg" />
                Your browser does not support the audio element.
              </audio>
            ) : (
              <p>No music selected</p>
            )}
          </Col>
        </Row>
      </motion.div>
    </Container>
  );
}
