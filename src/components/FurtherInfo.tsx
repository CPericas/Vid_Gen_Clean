import { useEffect } from "react";
import { Container, Row, Col, Button } from "react-bootstrap";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { usePrompt } from "../context/PromptContext";
import { useMode } from "../context/ModeContext";
import { useAvatar } from "../context/AvatarContext";
import { useSceneSettings } from "../context/SceneSettingsContext";

// Preloaded backgrounds and music
const preloadedBackgrounds = [
    "/backgrounds/background1.png",
    "/backgrounds/background2.png",
    "/backgrounds/background3.png",
    "/backgrounds/background4.png",
];

const musicOptions = [
    { label: "Fresh Focus", url: "/music/Fresh Focus.mp3"},
    { label: "Fright Night Twist", url: "/music/Fright Night Twist.mp3" },
    { label: "Monsters in Hotel", url: "/music/Monsters in Hotel.mp3" },
    { label: "New Hero in Town", url: "/music/New Hero in Town.mp3" },
    { label: "Wizard Circus", url: "/music/Wizard Circus.mp3" }
];

export default function FurtherInfo() {
    const { avatar } = useAvatar();
    const { prompt } = usePrompt();
    const { mode } = useMode();
    const navigate = useNavigate();
    const {
        selectedBackground,
        setSelectedBackground,
        selectedMusic,
        setSelectedMusic,
    } = useSceneSettings();

// auto selection for demo mode
    useEffect(() => {
        if (mode === "demo" && !selectedBackground && !selectedMusic ) {
          const demoBackground = "/backgrounds/background1.png";
          const demoMusic = "/music/Fresh Focus.mp3";
          setSelectedBackground(demoBackground);
          setSelectedMusic(demoMusic);
          navigate("/preview")
        }
      }, [mode, selectedBackground, selectedMusic, setSelectedBackground, setSelectedMusic, navigate]);

    const handleContinue = () => {
        if (selectedBackground && selectedMusic) {
        navigate("/preview");
        }
    };

    return (
        <Container className="py-5">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                {mode === "full" && (
                    <>
                        {/* Header */}
                        <Row className="justify-content-center mb-4">
                            <Col md={8} className="text-center">
                                <h2>Finalize Your Scene</h2>
                                <p className="lead">
                                    Choose a background and music style to match your cinematic avatar moment.
                                </p>
                            </Col>
                        </Row>

                        {/* Avatar preview */}
                        {avatar && (
                            <Row className="justify-content-center mb-4">
                                <Col md={4} className="text-center">
                                    <img
                                        src={avatar}
                                        alt="Selected Avatar"
                                        className="img-fluid rounded"
                                        style={{ maxHeight: "250px" }}
                                    />
                                </Col>
                            </Row>
                        )}

                        {/* Prompt preview */}
                        {prompt && (
                            <Row className="justify-content-center mb-4">
                                <Col md={4} className="text-center">
                                    <h5>Scene Description</h5>
                                    <p className="border rounded p-3 bg-light text-start">{prompt}</p>
                                </Col>
                            </Row>
                        )}

                        {/* Background selection */}
                        <Row className="justify-content-center mb-4">
                            <Col md={10}>
                                <h5 className="text-center mb-3">Choose a Background</h5>
                                <div className="d-flex justify-content-center gap-3 flex-wrap">
                                    {preloadedBackgrounds.map((bgUrl, i) => (
                                        <img
                                            key={i}
                                            src={bgUrl}
                                            alt={`Background ${i + 1}`}
                                            onClick={() => setSelectedBackground(bgUrl)}
                                            style={{
                                                width: "180px",
                                                height: "100px",
                                                objectFit: "cover",
                                                cursor: "pointer",
                                                border: selectedBackground === bgUrl ? "3px solid #0d6efd" : "1px solid #ccc",
                                                borderRadius: "10px",
                                                transition: "border 0.2s",
                                            }}
                                        />
                                    ))}
                                </div>
                            </Col>
                        </Row>

                        {/* Music selection */}
                        <Row className="justify-content-center mb-4">
                            <Col md={10}>
                                <div className="d-flex justify-content-center gap-3 flex-wrap">
                                    {musicOptions.map(({ label, url }, i) => (
                                        <div
                                            key={i}
                                            onClick={() => setSelectedMusic(url)}
                                            style={{
                                                padding: "10px 20px",
                                                borderRadius: "10px",
                                                cursor: "pointer",
                                                border: selectedMusic === url ? "3px solid #0d6efd" : "1px solid #ccc",
                                                backgroundColor: selectedMusic === url ? "#e7f1ff" : "#f8f9fa",
                                                userSelect: "none",
                                                minWidth: "120px",
                                                textAlign: "center",
                                                transition: "all 0.2s",
                                            }}
                                            tabIndex={0}
                                            onKeyDown={(e) => {
                                                if (e.key === "Enter" || e.key === " ") setSelectedMusic(url);
                                            }}
                                        >
                                            {label}
                                            <audio src={url} preload="none" controls style={{ marginTop: "8px", width: "100%" }} />
                                        </div>
                                    ))}
                                </div>
                            </Col>
                        </Row>
                        
                        <Row className="justify-content-center">
                            <Col md={6}  className="text-center">
                                <Button
                                    variant="primary"
                                    size="lg"
                                    disabled={!selectedBackground || !selectedMusic }
                                    onClick={handleContinue}
                                >
                                    Continue
                                </Button>
                            </Col>
                        </Row>
                    </>
                )}

            </motion.div>
        </Container>
    );
}