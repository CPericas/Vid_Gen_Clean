import { motion } from "framer-motion";
import { Button, Container, Row, Col, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useMode } from "../context/ModeContext";

export default function HomePage() {
  const navigate = useNavigate();
  const { mode, setMode } = useMode();

  const toggleMode = () => {
    setMode(mode === "demo" ? "full" : "demo");
  }

  const handleStart = () => {
    navigate("/upload");
  };

  return (
    <Container className="py-5">
      <Row className="justify-content-center mb-4">
        <Col md={10} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="mb-4">Fake Cinematic Avatar Video Generator</h1>

            <Form.Check
              type="switch"
              id="mode-switch"
              label={`Mode: ${mode === "demo" ? "Demo" : "Full" }`}
              checked={mode === "full"}
              onChange={toggleMode}
              className="mb-3"
            />

            <div className="mb-3">
              {/* Placeholder for demo video */}
              <div className="ratio ratio-16x9 border rounded shadow-sm">
                <video controls>
                  <source src="/demo.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>
            <Button variant="primary" size="lg" onClick={handleStart}>
              Try It Now
            </Button>
          </motion.div>
        </Col>
      </Row>

      <Row className="justify-content-center mt-5">
        <Col md={10} lg={8}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <h2>How It Works</h2>
            <p className="lead">
              Upload or choose an avatar, enter a short scene description, and generate a cinematic video with synced lip movement, voiceover, subtitles, and music. All with no cloud GPU or API costs.
            </p>
            <ul>
              <li>🎭 Avatar Upload or Selection</li>
              <li>🗣️ Text-to-Speech Voiceover</li>
              <li>🎬 AI Lip Sync</li>
              <li>📽️ Backgrounds + Cinematic Movement</li>
              <li>🎼 Subtitles + Background Music</li>
              <li>🔄 Preview or Pre-rendered Download</li>
            </ul>
          </motion.div>

          <div className="text-center mt-4">
            <Button variant="success" size="lg" onClick={handleStart}>
              Get Started Now
            </Button>
          </div>
        </Col>
      </Row>
    </Container>
  );
}
