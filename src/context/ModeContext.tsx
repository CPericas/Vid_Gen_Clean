import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

type Mode = 'demo' | 'full';

interface ModeContextType {
    mode: Mode;
    setMode: (mode: Mode) => void;
}

const  ModeContext = createContext<ModeContextType | undefined>(undefined);

export const ModeProvider = ({ children }: { children: ReactNode }) => {
    const [mode, setMode] = useState<Mode>('demo');

    return (
        <ModeContext.Provider value={{ mode, setMode }}>
            {children}
        </ModeContext.Provider>
    );
};

export const useMode = (): ModeContextType => {
    const context = useContext(ModeContext);
    if (!context) {
        throw new Error('useMode must be used within a ModeProvider');
    }
    return context;
}