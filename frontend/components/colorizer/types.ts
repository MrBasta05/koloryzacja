export interface Adjustments {
  hue: number;
  sepia: number;
  saturation: number;
  brightness: number;
  contrast: number;
}

export const DEFAULT_ADJUSTMENTS: Adjustments = {
  hue: 0,
  sepia: 0,
  saturation: 100,
  brightness: 100,
  contrast: 100,
};
