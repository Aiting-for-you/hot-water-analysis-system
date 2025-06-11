/// <reference types="vite/client" />

declare module '*.jsx' {
    import React from 'react';
    const component: React.FC<any>;
    export default component;
} 