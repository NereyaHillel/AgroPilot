export type Farm = { id: string; name: string };

export type Plot = {
  id: string;
  farm_id: string;
  name: string;
  area_m2: number;
  crop_id: string;
  planting_date: string;
  soil_id: string;
  row_spacing_m: number;
  emitter_spacing_m: number;
  emitter_id: string;
  lat: number;
  lon: number;
};

export type PlanDay = {
  date: string;
  et0_mm: number;
  kc: number;
  need_mm: number;
  litres: number;
  run_minutes: number;
  stale: boolean;
  bucket_end_mm: number;
};

export type Plan = {
  plot_id: string;
  bucket_capacity_mm: number;
  trigger_mm: number;
  days: PlanDay[];
};
