import { writable } from 'svelte/store'

export interface ImageConfig {
    url: string;
    size: number;
    padding: number;
}

export interface Arc {
    path: string;
    clipPath: string;
    name: string;
    image: ImageConfig;
    centerX: number;
    centerY: number;
    angleWidth: number;
    innerRadius: number;
    outerRadius: number;
    startAngle: number;
    endAngle: number;
    level: number;
}
  
export const selectedArcs = writable<Arc[]>([]);