import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

type SceneSettingsContextType = {
    selectedBackground: string | null;
    setSelectedBackground: (bg: string | null) => void;
    selectedMusic: string | null;
    setSelectedMusic: (music: string | null) => void;
};

const SceneSettingsContext = createContext<SceneSettingsContextType | undefined>(undefined);

export const SceneSettingsProvider = ({children}: {children: ReactNode}) => {
    const [selectedBackground, setSelectedBackground] = useState<string | null>(null);
    const [selectedMusic, setSelectedMusic] = useState<string | null>(null);

    return (
        <SceneSettingsContext.Provider value={{
            selectedBackground, setSelectedBackground, 
            selectedMusic, setSelectedMusic
         }}>
            {children}
        </SceneSettingsContext.Provider>
    );
};

export const useSceneSettings = () => {
    const context = useContext(SceneSettingsContext);
    if (!context) throw new Error("useSceneSettings must be used within sceneSettingsProvider");
    return context;
};