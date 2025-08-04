import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

type PromptContextType = {
    prompt: string | null;
    setPrompt: (url: string | null ) => void;
};

const PromptContext = createContext<PromptContextType | undefined>(undefined);

export const PromptProvider = ({ children }: { children: ReactNode}) => {
    const [prompt, setPrompt] = useState<string | null>(null);

    return (
        <PromptContext.Provider value={{ prompt, setPrompt }}>
            {children}
        </PromptContext.Provider>
    );
};

export const usePrompt = () => {
    const context = useContext(PromptContext);
    if (!context) throw new Error("usePrompt must be used within PromptProvider");
    return context;
};