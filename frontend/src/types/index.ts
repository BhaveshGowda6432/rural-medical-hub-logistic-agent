export type Village = {
  village_id: string;
  name: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  road_condition: string;
};

export type ClinicSummary = {
  clinic_id: string;
  villages_assigned: string[];
  route: string[];
  total_distance: number;
  coverage_score: number;
  allocated_resources: Record<string, number>;
  route_coordinates: Array<{ name: string; latitude: number; longitude: number }>;
};

export type OptimizeResult = {
  status: string;
  villages: Village[];
  clinics: ClinicSummary[];
  resources: Record<string, number>;
};
