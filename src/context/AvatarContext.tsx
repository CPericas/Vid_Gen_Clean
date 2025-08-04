import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

type AvatarContextType = {
    avatar: string | null;
    setAvatar: (url: string | null) => void;
};

const AvatarContext = createContext<AvatarContextType | undefined>(undefined);

export const AvatarProvider = ({ children }: { children: ReactNode}) => {
    const [avatar, setAvatar] = useState<string | null>(null);



    
    return (
        <AvatarContext.Provider value={{ avatar, setAvatar }}>
            {children}
        </AvatarContext.Provider>
    );
};

export const useAvatar = () => {
    const context = useContext(AvatarContext);
    if (!context) throw new Error("useAvatar must be used within AvatarProvider");
    return context;
};