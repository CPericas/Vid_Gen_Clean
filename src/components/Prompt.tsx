import { useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { Container, Row, Col, Form, Button, Image } from "react-bootstrap";
import { motion } from "framer-motion";
import { useAvatar } from "../context/AvatarContext";
import { usePrompt } from "../context/PromptContext";
import { useMode } from "../context/ModeContext";

export default function Prompt() {
  const { avatar } = useAvatar();
  const {prompt, setPrompt} = usePrompt();
  const { mode } = useMode();
  const navigate = useNavigate();

// In demo mode, auto-fill the prompt and move to scene step
  useEffect(() => {
    if (mode === "demo" && !prompt) {
      const demoPrompt = "This is a demonstration of my awesome abilities!";
      setPrompt(demoPrompt);
      navigate("/scene")
    }
  }, [mode, prompt, setPrompt, navigate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate("/scene");
  };

  return (
    <Container className="py-5">
      <motion.div
        initial={{ opacity: 0, y:20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        {mode === "full" && (
          <>

          {/* Avatar preview */}
            <Row className="justify-content-center mb-4">
              <Col md={6} className="text-center">
                {avatar ? (
                  <Image
                    src={avatar}
                    alt="Selected Avatar"
                    rounded
                    fluid
                    style={{ maxHeight: "300px" }}
                  />
                ): (
                  <p>No avatar selected</p>
                )}
              </Col>
            </Row>

            {/* Scene prompt form */}
            <Row className="justify-content-center">
              <Col md={6}>
                <Form onSubmit={handleSubmit}>
                  <Form.Group controlId="scenePrompt" className="mb-3">
                    <Form.Label>Enter your script (1 - 3 sentences): </Form.Label>
                    <Form.Control 
                      as="textarea"
                      rows={4}
                      value={prompt ?? ""}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="What should you avtar say?"
                      required
                    />
                  </Form.Group>

                    <div className="d-flex justify-content-center">
                      <Button type="submit" variant="primary" disabled={!prompt?.trim()}>
                        Continue 
                      </Button>
                    </div>
                </Form>
              </Col>
            </Row>
          </>
        )}
      </motion.div>
    </Container>    
  );
}
