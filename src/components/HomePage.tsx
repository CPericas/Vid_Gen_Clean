import { motion } from "framer-motion";
import { Button, Container, Row, Col, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useMode } from "../context/ModeContext";

export default function HomePage() {
  const navigate = useNavigate();
  const { mode, setMode } = useMode();

  // Toggle between demo or full mode 
  const toggleMode = () => {
    setMode(mode === "demo" ? "full" : "demo");
  }

  const handleStart = () => {
    navigate("/upload");
  };

  return (
    <Container className="py-5">
      {/*Hero Section */}
      <Row className="justify-content-center mb-4">
        <Col md={10} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <h1 className="mb-4">AI Video Generator SaaS Starter Kit  </h1>
            <h2 className="mb-4">Local-Only, No API Costs.</h2>
            <p className="lead">Fully working MVP built with React + Coqui TTS + SadTalker + FFmpeg.
              Generate cinematic talking avatar videos from text prompts — all locally.</p>

{/* Toggle between modes*/}
            <Form.Check
              type="switch"
              id="mode-switch"
              label={`Mode: ${mode === "demo" ? "Demo" : "Full" }`}
              checked={mode === "full"}
              onChange={toggleMode}
              className="mb-3"
            />

            <div className="mb-3">
              {/* Demo video */}
              <div className="ratio ratio-16x9 border rounded shadow-sm">
                <video controls>
                  <source src="/videos/Opening_Video.mp4" type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>
            </div>

            {/* CTA #1 */}
            <Button variant="primary" size="lg" onClick={handleStart}>
              Try It Now
            </Button>
          </motion.div>
        </Col>
      </Row>

{/* How it works Section */}
      <Row className="justify-content-center mt-5">
        <Col md={10} lg={8}>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <h2>How It Works</h2>
            <p className="lead">Build your own AI avatar video platform — ready to brand, run locally, and sell.</p>
            <p>
              Upload or choose an avatar, enter a short scene description, and generate a cinematic video with a background, synced lip movement, voiceover, and music. All with no cloud GPU or API costs.
            </p>
            <ul>
              <li>🎭 Avatar Upload or Selection</li>
              <li>🗣️ Text-to-Speech Voiceover</li>
              <li>🎬 AI Lip Sync</li>
              <li>📽️ Backgrounds + Cinematic Movement in preview</li>
              <li>🎼 Background Music</li>
              <li>🔄 Preview or Pre-rendered Download</li>
            </ul>
          </motion.div>

          <Row className="text-center mt-4">
            <Col sm={4}><img src="/pics/Avatar-Upload.png" className="img-fluid rounded shadow-sm" /></Col>
            <Col sm={4}><img src="/pics/prompt.png" className="img-fluid rounded shadow-sm" /></Col>
            <Col sm={4}><img src="/pics/Scene_Selector.png" className="img-fluid rounded shadow-sm" /></Col>
          </Row>




{/* CTA #2 */}
          <div className="text-center mt-4">
            <Button variant="success" size="lg" onClick={handleStart}>
              Get Started Now
            </Button>
          </div>
        </Col>
      </Row>

      <footer className="text-center text-muted mt-5">
        <small>© 2025 AI Video Generator MVP — Built by Chris Pericas</small>
      </footer>
    </Container>
  );
}
