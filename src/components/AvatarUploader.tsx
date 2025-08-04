import { useState } from "react";
import { useEffect } from "react";
import { motion } from "framer-motion";
import { Container, Row, Col, Form, Image } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useAvatar } from "../context/AvatarContext";
import { useMode } from "../context/ModeContext";

// Preloaded avatars to choose from (displayed in full mode)
const preloadedAvatars = [
  "/avatars/Avatar1.png",
  "/avatars/Avatar2.png",
  "/avatars/Avatar3.png",
];

export default function AvatarUploader() {
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null);
  const { setAvatar } = useAvatar();
  const { mode } = useMode();
  const navigate = useNavigate();

  useEffect(() => {
    // In demo mode, auto select avatar and navigate
    if (mode === "demo" && !selectedAvatar) {
      const demoAvatar = "/avatars/Avatar1.png";
      setSelectedAvatar(demoAvatar);
      setAvatar(demoAvatar);
      navigate("/prompt")
    }
    // Logging of selection for dev purposes. Can be removed in production
    if (selectedAvatar) {
    console.log("Selected avatar:", selectedAvatar);
    }
  }, [mode, selectedAvatar, setAvatar, navigate]);

  // Upload image and send to backend
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append("avatar", file);

      try {
        const res = await fetch("http://localhost:5001/upload-avatar", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();

        if (data.success && data.path) {
          setSelectedAvatar(data.path);
          setAvatar(data.path);
          navigate("/prompt");
        } else {
          console.error("Avatar upload was not successful");
        }
      } catch (err) {
        console.error("Upload error: ", err);
      }
    }
  };

  // selecting a pre loaded avatar
  const handleGallerySelect = (url: string) => {
    setSelectedAvatar(url);
    setAvatar(url);
    navigate("/prompt");
  };

  return (
    <Container className="py-5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-center mb-4">Upload or Choose Your Avatar</h2>

        {/* Only show upload/select options in full mode*/}
        {mode === "full" && (
          <>
            <Row className="justify-content-center mb-4">
              <Col md={6}>
                <Form.Label>Select an image file</Form.Label>
                <Form.Control 
                  type="file" 
                  accept="image/*" 
                  onChange={handleFileChange} 
                />
              </Col>
            </Row>

            <Row className="justify-content-center mb-4">
              <Col md={8}>
                <h5 className="text-center">Or choose from our sample avatars</h5>
                <div className="d-flex justify-content-center gap-3 flex-wrap">
                  {preloadedAvatars.map((url, i) => (
                    <Image
                      key={i}
                      src={url}
                      alt={`Avatar ${i + 1}`}
                      thumbnail
                      style={{
                        width: "100px",
                        cursor: "pointer",
                        border: selectedAvatar === url ? "2px solid #0d6efd" : "none",
                      }}
                      onClick={() => handleGallerySelect(url)}
                    />
                  ))}
                </div>
              </Col>
            </Row>
          </>
        )}
            
            {/*Show current selection */}
            {selectedAvatar && (
              <Row className="justify-content-center">
                <Col md={6} className="text-center">
                  <h5 className="mb-3">Selected Avatar</h5>
                  <Image
                    src={selectedAvatar}
                    alt="Selected Avatar"
                    rounded
                    fluid
                    style={{ maxHeight: "300px" }}
                  />
                </Col>
              </Row>
        )}
      </motion.div>
    </Container>
  );
}
