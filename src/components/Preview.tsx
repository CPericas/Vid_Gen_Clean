import { Container, Row, Col, Button } from "react-bootstrap";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { usePrompt } from "../context/PromptContext";
import { useAvatar } from "../context/AvatarContext";
import { useSceneSettings } from "../context/SceneSettingsContext";
import { useEffect, useState } from "react";

export default function Preview() {
    const { avatar } = useAvatar();
    const { prompt } = usePrompt();
    const navigate = useNavigate();
    const { selectedBackground, selectedMusic } = useSceneSettings();

    const [resolvedAvatarSrc, setResolvedAvatarSrc] = useState<string | null>(null);

    useEffect(() => {
        if (!avatar) {
            setResolvedAvatarSrc(null);
            return;
        }

        // If already absolute URL, just use it
        if (avatar.startsWith("http://") || avatar.startsWith("https://")) {
            setResolvedAvatarSrc(avatar);
            return;
        }

        // Try Flask path first
        const flaskUrl = `http://localhost:5001${avatar}`;
        const img = new Image();
        img.onload = () => setResolvedAvatarSrc(flaskUrl);
        img.onerror = () => setResolvedAvatarSrc(avatar); // fallback to frontend /public
        img.src = flaskUrl;
    }, [avatar]);

    return (
        <Container className="py-5">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >

                {/* Avatar preview */}
                <Row className="justify-content-center mb-4">
                    <Col md={6} className="text-center">
                        {resolvedAvatarSrc ? (
                            <motion.img
                                src={resolvedAvatarSrc}
                                alt="Selected Avatar"
                                className="img-fluid rounded"
                                style={{ maxHeight: "500px" }}
                                animate={{ y: [0, -10, 0], scale: [1, 1.02, 1] }}
                                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
                            />
                        ) : (
                            <p>No avatar selected</p>
                        )}
                    </Col>
                </Row>

                {/* Background preview with pan animation */}
                <Row className="justify-content-center py-5">
                    <Col md={6} className="text-center">
                        {selectedBackground ? (
                            <div
                                style={{
                                    width: "100%",
                                    height: "300px",
                                    overflow: "hidden",
                                    borderRadius: "10px",
                                    position: "relative",
                                    boxShadow: "0 0 15px rgba(0,0,0,0.3)",
                                }}
                            >
                                <motion.img
                                    src={selectedBackground}
                                    alt="Selected Background"
                                    style={{
                                        width: "120%",
                                        height: "100%",
                                        objectFit: "cover",
                                        position: "absolute",
                                        top: 0,
                                        left: 0,
                                    }}
                                    animate={{ x: ["0%", "-10%", "0%"] }}
                                    transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
                                />
                            </div>
                        ) : (
                            <p>No background selected</p>
                        )}
                    </Col>
                </Row>

                {/* Background music player */}
                <Row className="justify-content-center py-5">
                    <Col className="text-center" md={6}>
                        {selectedMusic ? (
                            <audio controls preload="auto" style={{ width: "100%" }}>
                                <source src={selectedMusic} type="audio/mpeg" />
                                Your browser does not support the audio element.
                            </audio>
                        ) : (
                            <p>No music selected</p>
                        )}
                    </Col>
                </Row>

                {/* Prompt preview */}
                <Row className="justify-content-center py-5">
                    <Col md={6} className="text-center">
                        {prompt ? (
                            <p
                                className="bg-dark text-white px-3 py-2 rounded"
                                style={{
                                    fontSize: "1.25rem",
                                    lineHeight: "1.6",
                                    display: "inline-block",
                                    maxWidth: "100%",
                                    wordWrap: "break-word",
                                    boxShadow: "0 0 10px rgba(0,0,0,0.5)",
                                }}
                            >
                                {prompt}
                            </p>
                        ) : null}
                    </Col>
                </Row>

                <Row className="justify-content-center">
                    <Col md={6} className="text-center">
                        <Button
                            variant="primary"
                            size="lg"
                            onClick={() => navigate("/generate")}
                        >
                            Continue
                        </Button>
                    </Col>
                </Row>

            </motion.div>
        </Container>
    )
}
